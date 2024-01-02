#!/bin/bash
uvicorn restful:app --env-file .env --reload
