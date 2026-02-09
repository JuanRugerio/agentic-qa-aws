# Agentic QA System (AWS Deployment)

## Tech Stack 
-LangChain

-Pinecone

-OpenAI

-AWS

-Python

-Docker

## Brief Overview
QA service leveraging RAG and Web Search as tools, hosted on AWS

## Introduction
This project is a production-style agentic Question Answering system that combines Retrieval-Augmented Generation (RAG) with real-time web search. The system dynamically decides whether to answer from uploaded documents or external sources, orchestrating tool use through LangChain and deploying a scalable ingestion + QA pipeline on AWS.

Users can upload documents through an API endpoint, which are embedded locally and indexed in a vector database. When a question is asked, the agent determines the best information source (private document corpus vs. web search), retrieves relevant context, and generates a grounded response using an LLM. An evaluation layer verifies that generated answers overlap with retrieved evidence to reduce hallucinations.

The system is designed as a distributed, event-driven architecture using containerized workers, message queues, and managed AWS services for scalability and observability.

## Key Features
Agentic QA with tool selection (RAG vs Web Search)

Document ingestion pipeline with async embedding workers

Local embeddings with Sentence Transformers (384-dim vectors)

Vector storage in Pinecone with metadata tracking

Prompt-engineered LLM responses

Automated answer evaluation against retrieved evidence

Full AWS deployment with monitoring and secrets management

Dockerized infrastructure for reproducibility


## Architecture Overview

The ingestion pipeline begins when a document is uploaded to an API Gateway endpoint and stored in S3. A Lambda function publishes a message to SQS, triggering an ECS Fargate worker that continuously consumes messages, generates embeddings locally, and upserts vectors with metadata into Pinecone. Metadata and ingestion logs are stored in DynamoDB.

For QA, an API endpoint receives user questions. The agent (LangChain orchestration) selects the appropriate tool: document retrieval or Google Programmable Search. Retrieved context is passed to an OpenAI LLM with an engineered prompt to produce grounded answers. A post-processing evaluation step checks semantic overlap between generated answers and retrieved content.

Monitoring and logging are handled via CloudWatch across Lambda and ECS services. Secrets are stored securely in AWS Secrets Manager. IAM roles control service access (S3, SQS, ECS). The system is fully containerized and exposed via an Application Load Balancer.


