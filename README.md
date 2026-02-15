# Medical Assistant AI

> An AI-powered content creation ecosystem for medical writers to generate accurate, high-quality, and compliant medical summaries and articles.

**Powered by AWS** | **Innovation Partner: H2S** | **Media Partner: YOURSTORY**

## Overview

Medical Assistant AI transforms fragmented medical literature into personalized, compliant content—solving the content creation crisis for medical writers through AI-powered workflow automation. The system reduces content creation time by 90% (hours → minutes) while ensuring enhanced accuracy through citation-backed, verified sources.

## The Problem We Solve

### 1. Fragmentation
Medical literature is scattered across thousands of journals, making manual research highly time-consuming and inefficient.

### 2. Human Error
Manual drafting risks:
- Missing critical details
- Using outdated guidelines
- Failing to validate sources effectively

## Our Solution

### Smart Aggregation
Combines search results from trusted repositories (PubMed Central), user-uploaded documents, and real-time industry trends into one unified dashboard.

### Hyper-Personalization
An engine that rewrites content based on specific medical personas (e.g., Oncologist vs. Pediatrician) to ensure tone and depth match the intended audience.

### Compliance First
Prioritizes evidence-backed outputs with full citations to minimize hallucinations and ensure accuracy.

## Key Features

### 1. Multi-Source Content Input
- **Unified Research**: Fetches papers from trusted repositories via clinical keyword search
- **Internal Data Integration**: Upload proprietary research & internal documents as source material

### 2. Hyper-Personalization Engine
- **Persona-Based Output**: Re-engineers content for specific audiences (Oncologist, GP, Pediatrician, Patient)
- **Customizable Parameters**: Controls Tone, Format, and Purpose
- Single dataset generates distinct narratives for different medical personas

### 3. Interactive Medical Assistant Chatbot
- **Context-Aware Q&A**: Ask questions directly about generated content or sources
- **Real-Time Refinement**: Use conversational commands for instant editing
- Source transparency with highlighted citations

### 4. Compliance & Risk Mitigation
- **Citation-Backed Outputs**: Every claim linked to a reference, minimizing hallucinations
- **Traceability**: Instant verification of original information sources
- Automated MLR (Medical, Legal, Regulatory) compliance checking

### 5. Visual Integration Suite
- **Smart Library**: Access built-in medical images or auto-extract figures/charts from uploaded papers
- Template-based image positioning

### 6. Real-Time Industry Trends
- **Live Updates**: Pulls trending research, drug approvals, & clinical alerts (past 24h-7 days)
- Dashboard integration for immediate access to latest medical developments

## User Journey

### 1. Discovery & Input (The Dashboard)
- View real-time medical updates and trends
- Choose input method: Keyword Search (PubMed Central) or Upload Documents

### 2. Curation & Configuration (The Setup)
- Review and select specific articles
- Configure target audience, tone, and depth
- Select image and layout template

### 3. Generation & Interactive Refinement (The Core)
- AI generates structured draft using TAP methodology (Think → Plan → Act)
- View highlighted chunks and citations for source transparency
- Interact with chatbot for Q&A and specific edits

### 4. Finalization (The Output)
- Preview and make manual edits
- Review MLR compliance report
- Export in preferred format (PDF, DOCX, HTML)

## Technology Stack

### Core & Frontend
- **Python**: Backend services and agent orchestration
- **React**: Modern, responsive user interface

### AWS Infrastructure & AI Services
- **Amazon Bedrock**: AI model deployment and orchestration
- **Anthropic Claude**: Advanced content generation and reasoning
- **S3 Bucket**: Secure storage for documents, images, and user uploads
- **EC2**: Application hosting and compute infrastructure

### AI Models & Vector Database
- **Qdrant (on AWS)**: Vector database for semantic search and retrieval
- **Anthropic Model (via Bedrock)**: State-of-the-art language model for content generation

## Target Users

### Primary Users
- Medical writers in pharmaceutical companies
- Healthcare content creators
- Clinical researchers and academic institutions
- Medical education platforms

### Expected Impact
- **90% time reduction** in medical content creation (hours → minutes)
- **Enhanced accuracy** through citation-backed, verified sources
- **Improved accessibility** via persona-based content adaptation
- **Reduced misinformation** through compliance checking

## Unique Selling Propositions

### 1. Beyond Generic AI
Closed-loop system using only verified medical sources (PubMed, internal repositories) - not generic web content.

### 2. Hyper-Personalization Engine
Single dataset generates distinct narratives for oncologists, GPs, and patients with appropriate terminology and depth.

### 3. Solving Data Fragmentation
Aggregates trusted repositories like PubMed Central into one dashboard, replacing manual journal searches.

### 4. Eliminating "Blank Page" Syndrome
Automates drafting phase by defining Content Requirements upfront, cutting time from hours to minutes.

### 5. Mitigating Risk
Provides Citation-Backed Outputs, linking every claim to a reference to solve the "Hallucination" problem.

### 6. Real-Time Relevance
Pulls live updates on drug approvals and trials, providing access to medical trends from the last 24 hours.

### 7. Integrated Visuals
Includes inbuilt image library and can extract figures from uploaded documents to create complete, cohesive article layouts.

## Architecture

The system follows a multi-agent orchestration pattern:

- **Agent Persona Registry**: Query Synthesizer, Compliance Checker, Scientific Persona Registry
- **Planning Agent**: Uses TAP Methodology (Think → Plan → Act) for intelligent orchestration
- **Content Writing Agent**: Generates citation-backed content with persona adaptation
- **MLR Check Pipeline**: Automated compliance validation
- **Knowledge Base**: Qdrant vector database synced with PubMed
- **Image Repository**: Mapped metadata for medical visuals

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- AWS Account with Bedrock access
- Qdrant instance

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/medical-assist.git
cd medical-assist

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install

# Configure AWS credentials
aws configure

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

```bash
# Start backend server
python app.py

# Start frontend (in separate terminal)
cd frontend
npm start
```

## Documentation

- [Requirements Document](.kiro/specs/medical-assistant-ai/requirements.md)
- [Design Document](.kiro/specs/medical-assistant-ai/design.md)
- [Implementation Tasks](.kiro/specs/medical-assistant-ai/tasks.md)

## Security & Compliance

- **Encryption at Rest**: AES-256 encryption for all stored documents
- **Encryption in Transit**: TLS 1.3 for all API communications
- **HIPAA Compliance**: Designed to meet HIPAA requirements for medical information
- **User Data Isolation**: Complete separation between user projects and documents
- **Audit Logging**: Comprehensive logging of all document access

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Powered by**: AWS
- **Innovation Partner**: H2S
- **Media Partner**: YOURSTORY
- Built for the **AI for Bharat Hackathon**

## Contact

For questions or support, please contact:
- Email: support@medical-assist.ai
- Website: https://medical-assist.ai

---

**Medical Assistant AI** - Transforming medical content creation through AI-powered workflow automation.
