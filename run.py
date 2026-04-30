#!/usr/bin/env python3
"""
Entry point para executar a aplicação FastAPI
Executa como: python run.py
"""
import sys
import os
import importlib

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    

    agent_module = importlib.import_module("nf-agent.agent_extractor")
    config_module = importlib.import_module("nf-agent.config")
    
    app = agent_module.app
    Config = config_module.Config
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9001,
        reload=Config.DEBUG,
    )
