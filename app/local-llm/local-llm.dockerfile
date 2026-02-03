FROM ollama/ollama:0.14.0

WORKDIR /app


EXPOSE 11434

#startup script to launch ollama and pull model
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Ollama service..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
echo "Waiting for Ollama to be ready..."\n\
sleep 5\n\
echo "Pulling phi3:mini model..."\n\
ollama pull phi3:mini\n\
echo "Model ready. Ollama service running on port 11434"\n\
wait $OLLAMA_PID' > /app/start.sh && chmod +x /app/start.sh

# Health check to ensure service is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1


ENTRYPOINT ["/bin/bash"]
CMD ["/app/start.sh"]