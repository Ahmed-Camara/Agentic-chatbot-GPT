# Agentic-chatbot-GPT

Chatbot agentique construit avec **LangGraph** et **LangChain**. L'agent s'appuie sur un LLM compatible OpenAI et peut appeler des outils externes : recherche web, calculatrice, cours de bourse, météo et date/heure en temps réel.

> 🚧 **Projet en cours de développement** : les outils de l'agent sont implémentés (`src/tools/tools.py`). Le graphe de l'agent, l'API et l'interface sont à venir.

## Stack technique

| Composant | Rôle |
| --- | --- |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Orchestration de l'agent sous forme de graphe d'états |
| `langgraph-checkpoint-sqlite` | Persistance de la mémoire de conversation (SQLite) |
| [LangChain](https://github.com/langchain-ai/langchain) (`langchain`, `langchain-core`, `langchain-community`, `langchain-openai`) | Abstractions LLM, outils et intégrations |
| [Tavily](https://tavily.com/) (`tavily-python`, `langchain-tavily`) | Recherche web |
| [Chroma](https://www.trychroma.com/) (`chromadb`, `langchain-chroma`) | Base vectorielle pour le RAG |
| `pypdf`, `docx2txt`, `langchain-text-splitters` | Chargement et découpage des documents (PDF, DOCX) |
| [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn + Jinja2 | API et interface web |
| [Streamlit](https://streamlit.io/) | Interface de chat (alternative) |
| SQLAlchemy | Accès base de données |
| [LangSmith](https://smith.langchain.com/) | Traçage et observabilité (optionnel) |

## Outils de l'agent

Définis dans [src/tools/tools.py](src/tools/tools.py) avec le décorateur `@tool` de LangChain :

| Outil | Description | Service / clé requise |
| --- | --- | --- |
| `web_search` | Recherche d'informations récentes sur Internet (titre, URL, extrait) | Tavily — `TAVILY_API_KEY` |
| `calculator` | Évalue une expression mathématique simple (`2 + 2`, `math.sqrt(16)`…) | Aucune |
| `get_stock_price` | Dernier cours d'une action à partir de son symbole (`AAPL`, `TSLA`…) | Alpha Vantage — `ALPHA_VANTAGE` |
| `get_current_weather` | Météo actuelle d'une ville : conditions, température, humidité, pression, vent | OpenWeather — `OPEN_WEATHER_API_KEY` |
| `get_datetime_information` | Date et heure actuelles, jour de la semaine, veille et lendemain (fuseau par défaut : `Africa/Abidjan`) | Aucune |

## Structure du projet

```text
Agentic-chatbot-GPT/
├── app.py              # Point d'entrée de l'application
├── requirements.txt    # Dépendances Python
├── src/
│   ├── agents/         # Définition des agents et des graphes LangGraph
│   └── tools/
│       └── tools.py    # Outils mis à disposition de l'agent
├── .env                # Variables d'environnement (non versionné)
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
```

Pour désactiver l'environnement : `conda deactivate`.

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
TAVILY_API_KEY=         # web_search (Tavily)
ALPHA_VANTAGE=          # get_stock_price (Alpha Vantage)
OPEN_WEATHER_API_KEY=   # get_current_weather (OpenWeather)
YOU_API_KEY=            # Recherche web You.com (non utilisé pour l'instant)
```

> ⚠️ Ne versionnez jamais le fichier `.env` : il contient vos clés d'API.

## Lancement

Le point d'entrée `app.py` n'est pas encore implémenté. Les commandes de lancement seront ajoutées une fois l'API FastAPI ou l'interface Streamlit en place.

## Feuille de route

- [x] Outils de l'agent : recherche web, calculatrice, bourse, météo, date/heure (`src/tools`)
- [ ] Graphe de l'agent avec LangGraph (`src/agents`)
- [ ] Mémoire de conversation persistante (checkpoint SQLite)
- [ ] Brique RAG : ingestion de documents PDF/DOCX dans Chroma
- [ ] API FastAPI et interface de chat (`app.py`)

## Licence

Distribué sous licence Apache 2.0. Voir [LICENSE](LICENSE).
