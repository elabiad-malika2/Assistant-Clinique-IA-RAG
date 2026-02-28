# monitoring/prometheus_metrics.py

from prometheus_client import Counter, Gauge

# 1. Nombre de requêtes
RAG_REQUESTS_TOTAL = Counter('rag_requests_total', 'Nombre total de questions posées au RAG')

# 2. Nombre d'erreurs
RAG_ERRORS_TOTAL = Counter('rag_errors_total', 'Nombre total d erreurs lors de la génération')

# 3. Qualité des réponses (Jauges car la note monte et descend)
RAG_ANSWER_RELEVANCE = Gauge('rag_answer_relevance', 'Score de pertinence de la réponse')
RAG_FAITHFULNESS = Gauge('rag_faithfulness', 'Score de fidélité au contexte')