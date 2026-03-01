# Clinico-Canvas: AI-Powered Medical Content Creation

Clinico-Canvas is an AI-driven platform designed to help medical writers efficiently create accurate, personalized, and evidence-backed medical articles. By streamlining the research and drafting process, it minimizes the risk of outdated information and reduces the time spent on manual literature reviews.

## Overview

Medical writing is often fragmented and time-consuming, requiring writers to manually filter through thousands of journals[cite: 24, 26]. **Clinico-Canvas** solves this by integrating real-time research, document parsing, and hyper-personalized AI generation into a single workflow[cite: 20].

### Key Capabilities
* **Reduce Research Burden:** Automates the search and validation of medical sources[cite: 20].
* **Hyper-Personalization:** Tailors content for specific medical personas (e.g., Oncologists vs. Pediatricians)[cite: 10, 130].
* **Evidence-Backed:** Ensures all content is supported by verified citations to prevent hallucinations[cite: 20, 134].

---

## Features

The application functions through a distinct 3-Module workflow:

### Module 1: Gather & Select Sources
* **Smart Search:** Query trusted repositories (e.g., PubMed Central) directly from the interface[cite: 53].
* **Document Upload:** Drag-and-drop internal research papers (PDFs) or notes[cite: 54].
* **Trend Analysis:** View trending medical research from the past 24 hours to 7 days[cite: 55, 139].
* **Internal Vector DB:** Supports fast retrieval of context from uploaded documents.

### Module 2: Define Content Requirements
* **Audience Targeting:** Customize content depth and tone for specific readers:
    * *Oncologist:* Data-heavy, molecular precision, trial data[cite: 106, 110].
    * *Pediatrician:* Child-centric, parent education, dosage safety[cite: 107, 111].
    * *General Physician:* Symptom recognition and referral criteria[cite: 108, 112].
* **Parameter Control:** Set tone (Scientific, Empathetic), format (Short Summary, Slide Copy), and region (US, EU, India)[cite: 57].

### Module 3: Generate & Refine
* **AI Drafting:** Generates structured content (IMRAD, Whitepaper, etc.) based on selected sources[cite: 37].
* **Interactive Refinement:** Embedded AI Chatbot to tweak tone or expand sections (e.g., "Make the tone more empathetic")[cite: 73].
* **Citation Management:** Auto-generated inline citations linked to source PDFs[cite: 74, 133].
* **Visuals:** Integrated image library and extraction of figures from uploaded papers[cite: 67, 68].
* **Export:** Download final drafts in PDF, DOCX, or Markdown[cite: 76].

---

## Tech Stack

* **Framework:** Next.js (React)
* **Styling:** Tailwind CSS
* **Backend:** FastAPI
* **AI Integration:** LLM Integration (OpenAI/Anthropic)
* **Database:** Vector Database (for RAG implementation) 
* **Document Parsing:** PDF extraction tools

---


## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone [https://code.involead.com/epocrates/epocrates.git](https://code.involead.com/epocrates/epocrates.git)
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up Environment Variables:**
    Create a `.env.local` file and add your API keys (LLM Provider, Database URL).

4.  **Run the development server:**
    ```bash
    npm run dev
    ```

5.  Open [http://localhost:3000](http://localhost:3000) with your browser.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.