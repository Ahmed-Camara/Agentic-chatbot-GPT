# Agentic-chatbot-GPT

Chatbot agentique construit avec **LangGraph** et **LangChain**. L'agent s'appuie sur un LLM compatible OpenAI et peut appeler des outils externes : recherche web, calculatrice, cours de bourse, météo et date/heure en temps réel.

> 🚧 **Projet en cours de développement** : les outils de l'agent sont implémentés (`src/tools/tools.py`) et l'arborescence est en place. Le graphe de l'agent, le RAG, la base de données, l'API et l'interface sont à venir.

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
├── app.py                  # Point d'entrée de l'application (FastAPI)
├── requirements.txt        # Dépendances Python
├── src/
│   ├── agents/
│   │   └── agent.py        # Graphe de l'agent LangGraph
│   ├── db/
│   │   └── database.py     # Accès base de données (SQLAlchemy / SQLite)
│   ├── rag/
│   │   └── rag.py          # Ingestion de documents et recherche dans Chroma
│   └── tools/
│       └── tools.py        # Outils mis à disposition de l'agent
├── templates/
│   └── index.html          # Interface de chat (template Jinja2)
├── .env                    # Variables d'environnement (non versionné)
└── LICENSE
```

| Module | État |
| --- | --- |
| `src/tools/tools.py` | ✅ Implémenté |
| `src/agents/agent.py` | 🚧 À implémenter |
| `src/rag/rag.py` | 🚧 À implémenter |
| `src/db/database.py` | 🚧 À implémenter |
| `templates/index.html` | 🚧 À implémenter |
| `app.py` | 🚧 À implémenter |

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
- [x] Arborescence du projet : `agents`, `rag`, `db`, `templates`
- [ ] Graphe de l'agent avec LangGraph (`src/agents/agent.py`)
- [ ] Mémoire de conversation persistante : checkpoint SQLite (`src/db/database.py`)
- [ ] Brique RAG : ingestion de documents PDF/DOCX dans Chroma (`src/rag/rag.py`)
- [ ] API FastAPI (`app.py`) et interface de chat (`templates/index.html`)

## Licence

Distribué sous licence Apache 2.0. Voir [LICENSE](LICENSE).
