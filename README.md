# Agentic-chatbot-GPT

**CGPT** est un chatbot agentique inspiré de ChatGPT, construit avec **LangGraph**, **LangChain** et **FastAPI**. L'agent s'appuie sur un LLM compatible OpenAI et choisit lui-même quand appeler ses outils :

- recherche web ;
- recherche dans vos documents (RAG) ;
- mémoire à long terme ;
- calculatrice ;
- cours de bourse ;
- météo ;
- date et heure.

Les réponses s'affichent en streaming dans une interface web de type ChatGPT.

## Fonctionnalités

- 💬 **Chat en streaming** : la réponse s'affiche mot à mot (Server-Sent Events). Le rendu Markdown est complet, avec coloration syntaxique du code.
- 🧠 **Agent outillé** : le LLM décide d'appeler un ou plusieurs outils, puis formule sa réponse à partir de leurs résultats.
- 📄 **RAG sur vos documents** : vous pouvez importer un ou plusieurs fichiers à la fois (PDF, DOCX, TXT, MD, PY, CSV), avec le bouton trombone ou par glisser-déposer. Les documents sont découpés, vectorisés et stockés dans Chroma. La recherche est limitée à la conversation courante.
- 🗂️ **Historique des conversations** : les conversations sont listées dans la barre latérale. Chacune peut être rouverte avec ses messages.
- 🔁 **Mémoire de conversation** : l'état du graphe est sauvegardé par `thread_id` grâce au checkpoint SQLite de LangGraph.
- 📌 **Mémoire à long terme** : « Souviens-toi que… » enregistre une information, que l'agent pourra retrouver plus tard.
- 🎙️ **Saisie vocale** : la dictée passe par la Web Speech API du navigateur (français par défaut).
- 🔀 **Choix du modèle** depuis l'interface.

## Stack technique

| Composant | Rôle |
| --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Orchestration de l'agent sous forme de graphe d'états |
| `langgraph-checkpoint-sqlite` | Persistance de l'état des conversations (`SqliteSaver`) |
| [LangChain](https://github.com/langchain-ai/langchain) (`langchain`, `langchain-core`, `langchain-community`, `langchain-openai`) | Abstractions LLM, outils et intégrations |
| [Tavily](https://tavily.com/) (`tavily-python`, `langchain-tavily`) | Recherche web |
| [Chroma](https://www.trychroma.com/) (`langchain-chroma`) + `OpenAIEmbeddings` | Base vectorielle du RAG |
| `pypdf`, `docx2txt`, `langchain-text-splitters` | Lecture et découpage des documents |
| [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn + Jinja2 + `python-multipart` | API, streaming SSE, upload et rendu de l'interface |
| SQLAlchemy (SQLite) | Conversations, messages et mémoire à long terme |
| HTML / CSS / JavaScript (marked, DOMPurify, highlight.js) | Interface de chat |
| [LangSmith](https://smith.langchain.com/) | Traçage et observabilité (optionnel) |

## Outils de l'agent

Définis dans [src/tools/tools.py](src/tools/tools.py) avec le décorateur `@tool` de LangChain :

| Outil | Description | Service / clé requise |
| --- | --- | --- |
| `web_search` | Recherche d'informations récentes sur Internet (titre, URL, extrait) | Tavily : `TAVILY_API_KEY` |
| `search_uploaded_documents` | Recherche dans les documents importés de la conversation courante (4 extraits les plus proches) | Embeddings : `EMBEDDING_MODEL` |
| `remember_this` | Enregistre une préférence ou un fait important dans la mémoire à long terme | Aucune |
| `recall_memory` | Retrouve les souvenirs enregistrés pour la conversation (20 derniers) | Aucune |
| `calculator` | Évalue une expression mathématique simple (`2 + 2`, `math.sqrt(16)`…) | Aucune |
| `get_stock_price` | Dernier cours d'une action à partir de son symbole (`AAPL`, `TSLA`…) | Alpha Vantage : `ALPHA_VANTAGE` |
| `get_current_weather` | Météo actuelle d'une ville : conditions, température, humidité, pression, vent | OpenWeather : `OPEN_WEATHER_API_KEY` |
| `get_datetime_information` | Date et heure actuelles, jour de la semaine, veille et lendemain (fuseau par défaut : `Africa/Abidjan`) | Aucune |

Les outils RAG et mémoire savent à quelle conversation ils s'appliquent grâce à `set_current_thread_id()`, appelé par l'API avant chaque exécution de l'agent.

## Prompt système

Le comportement de l'assistant est défini dans [src/agents/prompt.py](src/agents/prompt.py) (`SYSTEM_PROMPT`). L'assistant s'appelle **CGPT** et suit ces règles :

| Situation | Comportement attendu |
| --- | --- |
| Actualités, événements récents, prix actuels | `web_search`, en précisant que la réponse s'appuie sur des résultats web |
| Question sur un document importé | `search_uploaded_documents` |
| « Souviens-toi de… » | `remember_this` |
| Question sur des préférences ou des faits enregistrés | `recall_memory` |
| Calcul mathématique | `calculator` |
| Autres questions | Réponse directe, claire et concise |

## Architecture

### Graphe de l'agent

L'agent est un graphe d'états LangGraph (`StateGraph(MessagesState)`), construit dans [src/agents/agent.py](src/agents/agent.py) :

![Graphe LangGraph de l'agent](imgs/graph.png)

> ℹ️ Le schéma date de la conception du graphe et montre une arête `tools` → `__end__`. Dans le code final, l'arête est `tools` → `chat_node` (voir le flux ci-dessous). Pour régénérer le schéma : `get_agent().get_graph().draw_mermaid_png()`.

| Nœud | Rôle |
| --- | --- |
| `__start__` | Point d'entrée : reçoit le message de l'utilisateur |
| `chat_node` | Ajoute le prompt système, puis appelle le LLM (`ChatOpenAI`, avec les outils liés par `bind_tools`). Le modèle répond directement ou demande l'appel d'un outil |
| `tools` | `ToolNode` qui exécute les outils demandés par le LLM |
| `__end__` | Fin de l'exécution du graphe |

**Flux :**

1. `__start__` → `chat_node` : le message entre dans le graphe.
2. `chat_node` → `tools` ou `__end__` : le routage conditionnel `tools_condition` envoie vers `tools` si le LLM a demandé un outil, sinon vers `__end__`.
3. `tools` → `chat_node` : les résultats des outils sont renvoyés au LLM. Celui-ci peut alors appeler d'autres outils ou rédiger la réponse finale.

**Mémoire de conversation :** le graphe est compilé avec un `SqliteSaver` (`src/data/langgraph_checkpoints.sqlite`). L'historique est donc conservé par `thread_id`.

**Cache des agents :** `get_agent(model)` construit un agent par modèle à la première demande, puis le réutilise.

### Parcours d'un message

```text
Navigateur (index.html)
  │  POST /chat/stream  { message, thread_id, model }
  ▼
FastAPI (app.py)
  ├─ create_or_update_conversation / save_chat_message   → SQLite (chatbot_memory.db)
  ├─ set_current_thread_id(thread_id)                     → outils RAG et mémoire
  └─ agent.stream(..., stream_mode="messages")
        ├─ chat_node  → LLM
        └─ tools      → Tavily, Chroma, SQLite, APIs météo/bourse…
  │  data: {"token": "..."}  …  data: {"done": true}
  ▼
Navigateur : affichage progressif, puis rechargement de la liste des conversations
```

Seuls les morceaux de texte produits par le LLM sont envoyés au navigateur. Les appels d'outils et leurs résultats sont filtrés par `should_stream_chunk` ([src/utils/utils.py](src/utils/utils.py)).

### Stockage local

Tout est stocké dans `src/data/`, créé automatiquement au démarrage :

| Chemin | Contenu |
| --- | --- |
| `src/data/chatbot_memory.db` | Conversations, messages et mémoire à long terme (SQLAlchemy) |
| `src/data/langgraph_checkpoints.sqlite` | État des graphes LangGraph par `thread_id` |
| `src/data/uploads/` | Fichiers importés |
| `src/data/chroma_db/` | Base vectorielle Chroma (collection `agentic_chatbot_docs`) |

Les chemins des uploads et de Chroma sont définis dans [src/utils/variables.py](src/utils/variables.py).

## API

| Méthode | Route | Description |
| --- | --- | --- |
| `GET` | `/` | Interface de chat (`templates/index.html`) |
| `GET` | `/conversations` | Liste des conversations, de la plus récente à la plus ancienne |
| `GET` | `/history/{thread_id}` | Messages d'une conversation (`role`, `content`) |
| `POST` | `/upload` | Import d'un document (`multipart/form-data` : `file`, `thread_id`). Répond `{ "success": bool, "message": str }` |
| `POST` | `/chat/stream` | Envoi d'un message (JSON : `message`, `thread_id`, `model`). Répond en `text/event-stream` |

Format du flux de `/chat/stream` :

```text
data: {"token": "Bonjour"}
data: {"token": " !"}
data: {"done": true}
```

En cas d'erreur pendant la génération, le flux contient `data: {"error": "..."}` suivi de `data: {"done": true}`. Un message vide ou un JSON invalide renvoie un HTTP 400.

> L'import de plusieurs documents est géré par l'interface. Elle envoie les fichiers à `/upload` **un par un**, dans l'ordre, pour éviter les écritures concurrentes dans SQLite et Chroma.

## Structure du projet

```text
Agentic-chatbot-GPT/
├── app.py                  # API FastAPI : routes, upload, streaming SSE
├── requirements.txt        # Dépendances Python
├── src/
│   ├── agents/
│   │   ├── agent.py        # Graphe LangGraph, modèles autorisés, cache des agents
│   │   └── prompt.py       # Prompt système de l'assistant (SYSTEM_PROMPT)
│   ├── data/               # Données locales (créé au démarrage, voir « Stockage local »)
│   ├── db/
│   │   └── database.py     # Modèles SQLAlchemy : conversations, messages, mémoire
│   ├── rag/
│   │   └── rag.py          # Lecture, découpage, indexation et recherche dans Chroma
│   ├── states/
│   │   └── state.py        # État personnalisé ChatState (non utilisé : le graphe utilise MessagesState)
│   ├── tools/
│   │   └── tools.py        # Outils de l'agent
│   └── utils/
│       ├── utils.py        # Filtrage des morceaux streamés et format SSE
│       └── variables.py    # Chemins des uploads et de Chroma
├── templates/
│   └── index.html          # Interface de chat (HTML/CSS/JS)
├── imgs/
│   └── graph.png           # Schéma du graphe LangGraph
├── .env                    # Variables d'environnement (non versionné)
└── LICENSE
```

## Installation

Prérequis : [Anaconda](https://www.anaconda.com/) ou [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

```bash
git clone <url-du-depot>
cd Agentic-chatbot-GPT

# Créer l'environnement conda avec Python 3.12
conda create -n <nom_conda> python=3.12 -y

# Activer l'environnement
conda activate <nom_conda>

# Installer les dépendances
pip install -r requirements.txt
pip install langchain-chroma
```

> ℹ️ `langchain-chroma`, utilisé par `src/rag/rag.py`, ne figure pas encore dans `requirements.txt`. Il faut donc l'installer à part.

Pour désactiver l'environnement : `conda deactivate`.

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# LLM principal (API compatible OpenAI)
BASE_URL=
MODEL=
API_KEY=

# Embeddings (RAG). Ils utilisent aussi API_KEY
EMBEDDING_MODEL=
EMBEDDING_BASE_URL=

# LangSmith (optionnel)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

# Clés des outils
TAVILY_API_KEY=         # web_search (Tavily)
ALPHA_VANTAGE=          # get_stock_price (Alpha Vantage)
OPEN_WEATHER_API_KEY=   # get_current_weather (OpenWeather)

# Optionnelles, non utilisées par l'application pour l'instant
BASE_URL_ANT=
MODEL_ANT=
API_KEY_ANT=
GEM_MODEL=
GEM_API_KEY=
YOU_API_KEY=
```

> ⚠️ Ne versionnez jamais le fichier `.env` : il contient vos clés d'API (il est déjà dans `.gitignore`).

### Modèles

Le modèle se choisit dans le menu de l'interface. Les modèles autorisés (`ALLOWED_MODELS` dans [src/agents/agent.py](src/agents/agent.py)) sont :

- `qwen3.8-flash`
- `qwen3.8-max`
- `deepseek-v4.1-flash`

Un nom de modèle absent de cette liste est remplacé par le modèle par défaut : la variable `MODEL`, ou `qwen3.8-flash` si elle n'est pas définie.

## Lancement

Depuis la **racine du projet**, avec l'environnement conda activé :

```bash
python app.py
```

Ouvrez ensuite <http://localhost:9009>. Le serveur Uvicorn écoute sur `0.0.0.0:9009`, avec rechargement automatique (`reload=True`).

Autre façon de lancer : `uvicorn app:app --host 0.0.0.0 --port 9009 --reload`.

> ℹ️ Vérifiez que c'est bien le Python de l'environnement conda qui s'exécute (`where python` sous Windows, `which python` sous Linux/macOS). Un Python système risque de ne pas avoir les bonnes dépendances.

## Utilisation

1. **Nouvelle conversation** : cliquez sur « Nouvelle conversation » dans la barre latérale.
2. **Poser une question** : tapez votre message et appuyez sur Entrée. Maj+Entrée ajoute un saut de ligne. Le bouton ■ interrompt la génération.
3. **Dicter** : cliquez sur le micro et parlez. Le texte s'insère dans la zone de saisie. Cette fonction nécessite Chrome ou Edge, et l'autorisation d'accès au micro.
4. **Importer des documents** : cliquez sur le trombone et sélectionnez un ou plusieurs fichiers, ou glissez-les sur la zone de saisie. Posez ensuite vos questions sur leur contenu.
5. **Mémoriser** : « Souviens-toi que je préfère les réponses en français ».
6. **Reprendre une conversation** : cliquez sur une conversation de la barre latérale pour recharger son historique.

## Dépannage

| Problème | Cause probable / solution |
| --- | --- |
| `ModuleNotFoundError: No module named 'src'` | Le script est lancé depuis un sous-dossier. Lancez les commandes depuis la racine du projet (`python app.py`, ou `python -m src.agents.agent` pour un module). |
| `FileNotFoundError: [WinError 3] ... 'src\\data\\...'` | Le dossier `src/data` a été supprimé. Recréez-le (`mkdir src/data`) avant de relancer. |
| `Output data may contain inappropriate content.` dans le chat | La réponse a été bloquée par le filtre de contenu du fournisseur du modèle (Qwen). Reformulez la question, ouvrez une nouvelle conversation ou choisissez un autre modèle. |
| Le micro n'apparaît pas | Le navigateur ne prend pas en charge la Web Speech API. Utilisez Chrome ou Edge. |
| `No relevant uploaded document content found.` | Aucun document n'a été importé dans **cette** conversation. Le RAG est limité au `thread_id` courant. |

## Feuille de route

- [x] Outils de l'agent : recherche web, calculatrice, bourse, météo, date/heure
- [x] Prompt système de l'assistant CGPT
- [x] Graphe de l'agent avec LangGraph (`chat_node` ↔ `tools`) et cache par modèle
- [x] Mémoire de conversation persistante (checkpoint SQLite)
- [x] Mémoire à long terme : `remember_this`, `recall_memory`
- [x] RAG : import de documents (PDF, DOCX, TXT, MD, PY, CSV), indexation dans Chroma, outil `search_uploaded_documents`
- [x] API FastAPI : conversations, historique, upload, chat en streaming SSE
- [x] Interface web : streaming, Markdown, historique, choix du modèle, import de plusieurs documents, saisie vocale

## Licence

Distribué sous licence Apache 2.0. Voir [LICENSE](LICENSE).
