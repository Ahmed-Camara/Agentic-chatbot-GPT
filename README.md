# Agentic-chatbot-GPT

Chatbot agentique construit avec **LangGraph** et **LangChain**, servi via une interface **Streamlit**. L'agent s'appuie sur un LLM compatible OpenAI et peut appeler des outils externes (recherche web, données financières, météo…).

> 🚧 **Projet en cours de développement** : la structure est en place, l'implémentation des agents, des outils et de l'interface est à venir.

## Stack technique

| Composant | Rôle |
| --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Orchestration de l'agent sous forme de graphe d'états |
| [LangChain](https://github.com/langchain-ai/langchain) (`langchain-core`, `langchain-community`, `langchain-openai`) | Abstractions LLM, outils et intégrations |
| [Streamlit](https://streamlit.io/) | Interface de chat web |
| [LangSmith](https://smith.langchain.com/) | Traçage et observabilité (optionnel) |
| `python-dotenv` | Chargement des variables d'environnement |

## Structure du projet

```text
Agentic-chatbot-GPT/
├── app.py              # Point d'entrée de l'application Streamlit
├── requirements.txt    # Dépendances Python
├── src/
│   ├── agents/         # Définition des agents et des graphes LangGraph
│   └── tools/          # Outils mis à disposition de l'agent
├── .env                # Variables d'environnement (non versionné)
└── LICENSE
```

## Installation

Prérequis : Python 3.10+.

```bash
git clone <url-du-depot>
cd Agentic-chatbot-GPT

python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# LLM principal (API compatible OpenAI)
BASE_URL=
MODEL=
API_KEY=

# Modèle Gemini (optionnel)
GEM_MODEL=
GEM_API_KEY=

# Embeddings
EMBEDDING_MODEL=
EMBEDDING_BASE_URL=

# LangSmith (optionnel)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=

# Clés des outils
TAVILY_API_KEY=         # Recherche web (Tavily)
YOU_API_KEY=            # Recherche web (You.com)
ALPHA_VANTAGE=          # Données financières (Alpha Vantage)
OPEN_WEATHER_API_KEY=   # Météo (OpenWeather)
```

> ⚠️ Ne versionnez jamais le fichier `.env` : il contient vos clés d'API.

## Lancement

```bash
streamlit run app.py
```

L'application est ensuite accessible sur <http://localhost:8501>.

## Feuille de route

- [ ] Implémenter le graphe de l'agent avec LangGraph (`src/agents`)
- [ ] Ajouter les outils : recherche web, finance, météo (`src/tools`)
- [ ] Construire l'interface de chat Streamlit (`app.py`)
- [ ] Ajouter la mémoire de conversation
- [ ] Ajouter une brique RAG à partir des embeddings

## Licence

Distribué sous licence Apache 2.0. Voir [LICENSE](LICENSE).
