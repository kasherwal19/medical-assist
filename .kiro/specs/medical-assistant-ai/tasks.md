# Implementation Plan: Medical Assistant AI

## Overview

This implementation plan breaks down the Medical Assistant AI system into incremental, testable components. The system uses Python for backend services, React for the frontend, AWS infrastructure (Bedrock, S3, EC2), and Qdrant for vector database operations. Each task builds on previous work, with property-based tests integrated throughout to validate correctness properties from the design document.

The implementation follows a layered approach:
1. Core data models and infrastructure setup
2. Agent components (Query Synthesizer, Persona Engine, Content Generator, Compliance Checker)
3. Orchestration layer (Planning Agent, MLR Pipeline)
4. User-facing features (Chatbot, Trend Feed, Export)
5. Frontend integration and end-to-end workflows

## Tasks

- [ ] 1. Set up project infrastructure and core data models
  - Create Python project structure with virtual environment
  - Set up AWS SDK configuration for Bedrock, S3, and EC2
  - Initialize Qdrant vector database connection
  - Define core data models (Document, Citation, ContentDraft, Project, MedicalPersona, GenerationConfig)
  - Implement data model serialization/deserialization for persistence
  - Set up logging and error handling framework
  - _Requirements: 1.2, 13.6, 17.1_

- [ ]* 1.1 Write property test for data model serialization
  - **Property 23: Project Persistence Round-Trip**
  - **Validates: Requirements 13.6**

- [ ] 2. Implement Knowledge Base with Qdrant integration
  - [ ] 2.1 Create KnowledgeBase class with vector database operations
    - Implement document indexing with embeddings generation
    - Implement semantic search functionality
    - Implement document retrieval by ID
    - Implement document deletion
    - _Requirements: 1.2, 1.3, 12.1, 12.4_

  - [ ]* 2.2 Write property test for document upload integration
    - **Property 2: Document Upload Integration**
    - **Validates: Requirements 1.2, 1.4, 10.3**

  - [ ]* 2.3 Write property test for source traceability
    - **Property 3: Source Traceability**
    - **Validates: Requirements 1.3**

  - [ ]* 2.4 Write property test for metadata completeness
    - **Property 5 (partial): Citation Verification Round-Trip**
    - **Validates: Requirements 12.4**

  - [ ] 2.5 Implement PubMed synchronization
    - Create scheduled job for daily synchronization
    - Implement error handling and retry logic
    - _Requirements: 12.1, 12.2, 12.5_

  - [ ]* 2.6 Write property test for knowledge base synchronization
    - **Property 33: Knowledge Base Synchronization**
    - **Validates: Requirements 12.3**

- [ ] 3. Implement Query Synthesizer Agent
  - [ ] 3.1 Create QuerySynthesizer class with query optimization
    - Implement clinical keyword expansion with medical terminology
    - Implement Boolean operator application
    - Implement ambiguous term detection
    - Implement PubMed Central API integration
    - Implement result ranking by relevance
    - _Requirements: 1.1, 1.5, 14.1, 14.2, 14.3, 14.5_

  - [ ]* 3.2 Write property test for query-to-results mapping
    - **Property 1: Query-to-Results Mapping**
    - **Validates: Requirements 1.1, 1.5**

  - [ ]* 3.3 Write property test for query expansion
    - **Property 25: Query Expansion**
    - **Validates: Requirements 14.1**

  - [ ]* 3.4 Write property test for Boolean operator application
    - **Property 26: Boolean Operator Application**
    - **Validates: Requirements 14.2**

  - [ ]* 3.5 Write property test for zero-result alternatives
    - **Property 27: Zero-Result Alternative Suggestions**
    - **Validates: Requirements 14.5**

  - [ ]* 3.6 Write property test for ambiguous term clarification
    - **Property 39: Ambiguous Term Clarification**
    - **Validates: Requirements 14.3**

  - [ ]* 3.7 Write unit tests for PubMed API error handling
    - Test graceful degradation when PubMed is unavailable
    - Test timeout handling
    - _Requirements: 16.3_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Persona Engine
  - [ ] 5.1 Create Scientific Persona Registry with persona definitions
    - Define General Physician persona with characteristics
    - Define Pediatrician persona with characteristics
    - Define Oncologist persona with characteristics
    - Store persona profiles with expertise levels and terminology complexity
    - _Requirements: 2.2_

  - [ ] 5.2 Create PersonaEngine class with content adaptation
    - Implement persona loading from registry
    - Implement content adaptation based on persona, tone, depth, and format
    - Implement terminology complexity adjustment
    - Implement narrative structure modification
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6_

  - [ ]* 5.3 Write property test for persona adaptation distinctness
    - **Property 7: Persona Adaptation Distinctness**
    - **Validates: Requirements 2.1, 2.3**

  - [ ]* 5.4 Write property test for configuration parameter application
    - **Property 8: Configuration Parameter Application**
    - **Validates: Requirements 2.4, 2.5, 2.6**

  - [ ]* 5.5 Write unit test for persona registry
    - Test that all three required personas exist
    - _Requirements: 2.2_

- [ ] 6. Implement Content Generator Agent
  - [ ] 6.1 Create ContentGenerator class with Amazon Bedrock integration
    - Set up Bedrock client with Anthropic Claude model
    - Implement draft generation from sources and outline
    - Implement citation embedding for factual claims
    - Implement content structuring based on format parameters
    - Integrate with PersonaEngine for adaptation
    - _Requirements: 4.1, 7.4, 8.2_

  - [ ]* 6.2 Write property test for citation completeness
    - **Property 4: Citation Completeness**
    - **Validates: Requirements 4.1, 4.2, 4.4**

  - [ ]* 6.3 Write property test for content generation completeness
    - **Property 15: Content Generation Completeness**
    - **Validates: Requirements 7.4**

  - [ ] 6.2 Implement citation extraction and linking
    - Extract factual claims from generated content
    - Link claims to source document chunks
    - Generate formatted citation strings
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ]* 6.4 Write property test for citation verification round-trip
    - **Property 5: Citation Verification Round-Trip**
    - **Validates: Requirements 4.3**

- [ ] 7. Implement Compliance Checker Agent
  - [ ] 7.1 Create ComplianceChecker class with validation logic
    - Implement citation coverage validation
    - Implement unsupported claim detection
    - Implement regulatory concern flagging
    - Generate compliance reports with detailed findings
    - _Requirements: 4.4, 4.5, 9.2, 9.3_

  - [ ]* 7.2 Write property test for unsupported claim detection
    - **Property 6: Unsupported Claim Detection**
    - **Validates: Requirements 4.5, 9.2**

  - [ ]* 7.3 Write unit tests for compliance checker
    - Test detection of content with no citations
    - Test detection of partially cited content
    - Test regulatory flag identification
    - _Requirements: 4.5, 9.3_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement Planning Agent with TAP methodology
  - [ ] 9.1 Create PlanningAgent class with Think-Plan-Act workflow
    - Implement Think phase: analyze source documents and user intent
    - Implement Plan phase: create content outline and execution plan
    - Implement Act phase: coordinate agent execution
    - Implement conflict resolution for contradicting sources
    - Implement gap identification in source coverage
    - _Requirements: 8.1, 8.2, 8.3, 8.5_

  - [ ]* 9.2 Write property test for outline creation
    - **Property 17: Planning Agent Outline Creation**
    - **Validates: Requirements 8.2**

  - [ ]* 9.3 Write property test for gap notification
    - **Property 18: Gap Notification**
    - **Validates: Requirements 8.3**

  - [ ]* 9.4 Write property test for source conflict resolution
    - **Property 19: Source Conflict Resolution**
    - **Validates: Requirements 8.5**

- [ ] 10. Implement MLR Check Pipeline
  - [ ] 10.1 Create MLRPipeline class with automated compliance checks
    - Integrate with ComplianceChecker for validation
    - Implement citation sufficiency checks
    - Implement regulatory flag identification
    - Generate comprehensive compliance reports
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

  - [ ]* 10.2 Write property test for MLR compliance execution
    - **Property 20: MLR Compliance Execution**
    - **Validates: Requirements 9.1, 9.3, 9.4**

  - [ ]* 10.3 Write unit tests for MLR pipeline
    - Test compliance report generation
    - Test handling of content with warnings vs failures
    - _Requirements: 9.1, 9.4_

- [ ] 11. Implement Image Repository
  - [ ] 11.1 Create ImageRepository class with S3 integration
    - Implement image storage to S3 with metadata
    - Implement figure extraction from PDF documents
    - Implement image search by keywords
    - Implement metadata retrieval
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ]* 11.2 Write property test for image extraction and metadata
    - **Property 12: Image Extraction and Metadata**
    - **Validates: Requirements 5.2, 5.4**

  - [ ]* 11.3 Write property test for image relevance suggestion
    - **Property 37: Image Relevance Suggestion**
    - **Validates: Requirements 5.3**

  - [ ]* 11.4 Write property test for template-based image positioning
    - **Property 38: Template-Based Image Positioning**
    - **Validates: Requirements 5.6**

  - [ ]* 11.5 Write unit test for image repository access
    - Test that built-in image repository is accessible
    - _Requirements: 5.1_

- [ ] 12. Implement Trend Feed Service
  - [ ] 12.1 Create TrendFeedService class with real-time aggregation
    - Implement trending research fetching (24h-7 days)
    - Implement drug approval fetching from regulatory sources
    - Implement clinical alert aggregation
    - Implement feed update mechanism
    - _Requirements: 6.1, 6.2, 6.3, 6.5, 6.6_

  - [ ]* 12.2 Write property test for trend feed recency
    - **Property 13: Trend Feed Recency**
    - **Validates: Requirements 6.1**

  - [ ]* 12.3 Write property test for trend item incorporation
    - **Property 14: Trend Item Incorporation**
    - **Validates: Requirements 6.5**

  - [ ]* 12.4 Write unit tests for trend feed
    - Test that drug approvals appear in feed
    - Test that clinical alerts appear in feed
    - Test automatic feed updates
    - _Requirements: 6.2, 6.3, 6.6_

- [ ] 13. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Implement Interactive Chatbot
  - [ ] 14.1 Create InteractiveChatbot class with conversational interface
    - Implement query processing with context awareness
    - Implement edit command parsing and application
    - Implement citation information retrieval
    - Implement conversation context management
    - Integrate with Bedrock for natural language understanding
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 14.2 Write property test for context preservation
    - **Property 9: Chatbot Context Preservation**
    - **Validates: Requirements 3.4**

  - [ ]* 14.3 Write property test for conversational edit application
    - **Property 10: Conversational Edit Application**
    - **Validates: Requirements 3.2**

  - [ ]* 14.4 Write property test for claim-to-citation query
    - **Property 11: Claim-to-Citation Query**
    - **Validates: Requirements 3.5**

  - [ ]* 14.5 Write property test for chatbot source grounding
    - **Property 36: Chatbot Source Grounding**
    - **Validates: Requirements 3.1, 3.3**

- [ ] 15. Implement Export and Finalization
  - [ ] 15.1 Create ExportService class with multi-format support
    - Implement PDF export with citations and images
    - Implement DOCX export with citations and images
    - Implement HTML export with citations and images
    - Ensure all exports include properly formatted reference sections
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 7.8_

  - [ ]* 15.2 Write property test for export format preservation
    - **Property 16: Export Format Preservation**
    - **Validates: Requirements 7.8, 11.4, 11.5**

  - [ ]* 15.3 Write property test for multi-format export support
    - **Property 24: Multi-Format Export Support**
    - **Validates: Requirements 11.1, 11.2, 11.3**

  - [ ]* 15.4 Write unit tests for each export format
    - Test PDF export functionality
    - Test DOCX export functionality
    - Test HTML export functionality
    - _Requirements: 11.1, 11.2, 11.3_

- [ ] 16. Implement User Authentication and Project Management
  - [ ] 16.1 Create authentication system with AWS IAM integration
    - Implement user authentication with token-based auth
    - Implement authorization checks for resource access
    - Implement audit logging for all document access
    - _Requirements: 13.1, 17.3, 17.4_

  - [ ] 16.2 Create ProjectManager class with CRUD operations
    - Implement project creation
    - Implement project retrieval by user
    - Implement project opening/loading
    - Implement project deletion with cascade
    - Implement project saving with full state persistence
    - Implement auto-save mechanism
    - _Requirements: 13.2, 13.3, 13.4, 13.5, 13.6, 13.7_

  - [ ]* 16.3 Write property test for user project retrieval
    - **Property 34: User Project Retrieval**
    - **Validates: Requirements 13.2**

  - [ ]* 16.4 Write property test for project lifecycle operations
    - **Property 35: Project Lifecycle Operations**
    - **Validates: Requirements 13.3, 13.4, 13.5**

  - [ ]* 16.5 Write property test for user data isolation
    - **Property 31: User Data Isolation**
    - **Validates: Requirements 17.3**

  - [ ]* 16.6 Write property test for audit log completeness
    - **Property 32: Audit Log Completeness**
    - **Validates: Requirements 17.4**

  - [ ]* 16.7 Write unit test for authentication requirement
    - Test that unauthenticated access is blocked
    - _Requirements: 13.1_

- [ ] 17. Implement Security and Encryption
  - [ ] 17.1 Configure S3 encryption for document storage
    - Enable AES-256 encryption at rest for all S3 buckets
    - Configure KMS keys for encryption management
    - _Requirements: 17.1_

  - [ ] 17.2 Configure TLS for data in transit
    - Ensure all API endpoints use TLS 1.3
    - Configure certificate management
    - _Requirements: 17.2_

  - [ ]* 17.3 Write property test for document encryption at rest
    - **Property 30: Document Encryption at Rest**
    - **Validates: Requirements 17.1**

  - [ ]* 17.4 Write unit test for TLS configuration
    - Test that TLS 1.3 is enforced
    - _Requirements: 17.2_

- [ ] 18. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 19. Implement Orchestration Abstraction Layer
  - [ ] 19.1 Create OrchestrationLayer class coordinating all agents
    - Implement workflow orchestration for content generation
    - Integrate PlanningAgent, QuerySynthesizer, PersonaEngine, ContentGenerator, ComplianceChecker
    - Implement error handling and graceful degradation
    - Implement progress tracking and user notifications
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

  - [ ]* 19.2 Write unit tests for workflow orchestration
    - Test complete workflow from search to generation
    - Test workflow from upload to generation
    - _Requirements: 7.1, 7.2, 7.3_

- [ ] 20. Implement Error Handling Framework
  - [ ] 20.1 Create comprehensive error handling across all components
    - Implement graceful degradation for external service failures
    - Implement partial success handling for batch operations
    - Implement retry logic with exponential backoff
    - Implement validation before expensive operations
    - Implement consistent error response format
    - _Requirements: 16.1, 16.2, 16.3_

  - [ ]* 20.2 Write property test for error message descriptiveness
    - **Property 28: Error Message Descriptiveness**
    - **Validates: Requirements 16.1**

  - [ ]* 20.3 Write property test for graceful degradation
    - **Property 29: Graceful Degradation on Document Processing Failure**
    - **Validates: Requirements 16.2**

  - [ ]* 20.4 Write unit test for PubMed unavailability handling
    - Test graceful degradation when PubMed is unavailable
    - _Requirements: 16.3_

- [ ] 21. Implement REST API Layer
  - [ ] 21.1 Create Flask/FastAPI application with endpoints
    - Implement authentication endpoints (login, logout, token refresh)
    - Implement project management endpoints (CRUD operations)
    - Implement search endpoints (PubMed search, document upload)
    - Implement source selection endpoints
    - Implement content generation endpoints
    - Implement chatbot interaction endpoints
    - Implement export endpoints
    - Implement trend feed endpoints
    - Add request validation and error handling middleware
    - _Requirements: All user-facing requirements_

  - [ ]* 21.1 Write property test for search result metadata completeness
    - **Property 21: Search Result Metadata Completeness**
    - **Validates: Requirements 10.1**

  - [ ]* 21.2 Write property test for source selection reflection
    - **Property 22: Source Selection Reflection**
    - **Validates: Requirements 10.4**

  - [ ]* 21.3 Write unit tests for API endpoints
    - Test authentication flow
    - Test project CRUD operations
    - Test search and upload endpoints
    - Test generation endpoints
    - Test export endpoints
    - _Requirements: Various_

- [ ] 22. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 23. Implement React Frontend - Dashboard and Navigation
  - [ ] 23.1 Set up React project with TypeScript and routing
    - Initialize React app with Create React App or Vite
    - Set up React Router for navigation
    - Configure TypeScript for type safety
    - Set up state management (Redux or Context API)
    - Configure API client for backend communication
    - _Requirements: 6.4, 7.1_

  - [ ] 23.2 Create Dashboard component with trend feed
    - Implement dashboard layout
    - Implement trend feed display with real-time updates
    - Implement navigation to project creation
    - _Requirements: 6.4, 7.1_

  - [ ]* 23.3 Write unit tests for dashboard component
    - Test trend feed rendering
    - Test navigation functionality
    - _Requirements: 6.4_

- [ ] 24. Implement React Frontend - Project Creation and Source Selection
  - [ ] 24.1 Create project creation flow components
    - Implement input selection UI (keyword search vs document upload)
    - Implement keyword search interface with filters
    - Implement document upload interface with drag-and-drop
    - Implement source selection UI with checkboxes
    - Display article metadata (title, abstract, date, relevance)
    - _Requirements: 7.1, 7.2, 10.1, 10.2_

  - [ ]* 24.2 Write unit tests for source selection
    - Test that input options are presented
    - Test source selection/deselection
    - Test validation preventing generation with no sources
    - _Requirements: 7.1, 7.2, 10.2, 10.5_

- [ ] 25. Implement React Frontend - Configuration and Generation
  - [ ] 25.1 Create configuration interface
    - Implement persona selection dropdown
    - Implement tone, depth, and format selectors
    - Implement image selection from repository
    - Implement layout template selection
    - Display selected source count
    - _Requirements: 7.3, 5.5, 10.4_

  - [ ] 25.2 Create content generation and display components
    - Implement generation progress indicator
    - Implement content display with citation highlighting
    - Implement source transparency view
    - _Requirements: 7.5, 4.6, 16.4_

  - [ ]* 25.3 Write unit tests for configuration UI
    - Test configuration prompt display
    - Test image selection capability
    - _Requirements: 7.3, 5.5_

- [ ] 26. Implement React Frontend - Interactive Chatbot
  - [ ] 26.1 Create chatbot interface component
    - Implement chat message display
    - Implement message input with send button
    - Implement real-time message updates
    - Implement citation display in chat responses
    - Integrate with backend chatbot API
    - _Requirements: 3.1, 3.2, 3.3, 3.5, 7.6_

  - [ ]* 26.2 Write unit tests for chatbot UI
    - Test message sending and receiving
    - Test citation display in responses
    - _Requirements: 7.6_

- [ ] 27. Implement React Frontend - Review and Export
  - [ ] 27.1 Create review and editing interface
    - Implement content preview with manual editing
    - Implement MLR compliance report display
    - Implement issue highlighting with locations
    - Implement approval workflow
    - _Requirements: 7.7, 9.4, 9.5_

  - [ ] 27.2 Create export interface
    - Implement format selection (PDF, DOCX, HTML)
    - Implement export button with progress indicator
    - Implement download handling
    - _Requirements: 7.8, 11.1, 11.2, 11.3_

  - [ ]* 27.3 Write unit tests for review and export UI
    - Test preview and editing capabilities
    - Test MLR report display
    - Test approval workflow
    - _Requirements: 7.7, 9.5_

- [ ] 28. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 29. Integration and End-to-End Testing
  - [ ] 29.1 Write integration tests for complete workflows
    - Test end-to-end workflow: search → select → configure → generate → review → export
    - Test end-to-end workflow: upload → select → configure → generate → review → export
    - Test chatbot interaction during review phase
    - Test project save and reload
    - _Requirements: All workflow requirements_

  - [ ] 29.2 Write integration tests for external services
    - Test real PubMed Central API integration
    - Test real Amazon Bedrock integration
    - Test real Qdrant vector database operations
    - Test real S3 storage operations
    - _Requirements: 1.1, 6.1, 12.1, 17.1_

  - [ ]* 29.3 Perform manual testing of UI workflows
    - Test complete user journey in browser
    - Test responsive design on different screen sizes
    - Test error scenarios and user feedback
    - _Requirements: All UI requirements_

- [ ] 30. Deployment and Infrastructure Setup
  - [ ] 30.1 Configure AWS infrastructure
    - Set up EC2 instances for application hosting
    - Configure Application Load Balancer
    - Set up S3 buckets for documents and images with encryption
    - Configure IAM roles and policies
    - Set up KMS for encryption key management
    - Deploy Qdrant on EC2 or use managed service
    - Configure Amazon Bedrock access
    - _Requirements: 17.1, 17.2_

  - [ ] 30.2 Deploy application to AWS
    - Deploy Python backend to EC2
    - Deploy React frontend to S3 + CloudFront or EC2
    - Configure environment variables and secrets
    - Set up monitoring and logging (CloudWatch)
    - Configure auto-scaling policies
    - _Requirements: All infrastructure requirements_

  - [ ] 30.3 Set up CI/CD pipeline
    - Configure automated testing on commits
    - Configure automated deployment to staging
    - Configure manual approval for production deployment
    - _Requirements: Testing strategy_

- [ ] 31. Final Checkpoint - Complete System Validation
  - Run all unit tests, property tests, and integration tests
  - Verify all 39 correctness properties pass
  - Perform end-to-end testing in deployed environment
  - Verify security configurations (encryption, TLS, IAM)
  - Verify compliance with all requirements
  - Ask the user if any issues arise or if the system is ready for production

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at reasonable breaks
- Property tests validate universal correctness properties with 100+ iterations
- Unit tests validate specific examples, edge cases, and error conditions
- The implementation uses Python with `hypothesis` library for property-based testing
- Frontend uses React with TypeScript for type safety
- AWS infrastructure provides scalability and security
- All sensitive data is encrypted at rest (AES-256) and in transit (TLS 1.3)
