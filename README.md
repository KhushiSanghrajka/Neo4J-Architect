# Neo4j Architect

A comprehensive toolkit for analyzing, visualizing, and populating Neo4j databases with various data sources, enhanced with AI capabilities for intelligent data processing and querying.

## Repository Details
- **Name**: neo4j-architect
- **Purpose**: Tools for populating Neo4j databases from various sources and interacting with the data using AI
- **License**: MIT

## Aim/Purpose
This repository provides a collection of tools to:
1. Convert different data sources (JSON, PDF, Markdown, Python code) into Neo4j graph structures
2. Visualize code dependencies and relationships
3. Enable AI-powered querying of the graph database
4. Provide interactive visualization of data relationships

## Files Description and Usage

### Data Importers
- `json-to-graph.py`: Converts JSON data to Neo4j nodes and relationships with automatic schema detection
- `pdf-to-graph.py`: Extracts content from PDFs and creates knowledge graphs
- `md-to-graph`: Processes Markdown files into structured graph data
- `repo-to-graph.py`: Analyzes Python repositories and creates code structure graphs

### Visualization Tools
- `code-visualizer.py`: Creates static and interactive visualizations of code dependencies
  - Generates both PNG and interactive HTML visualizations
  - Shows hierarchical relationships, imports, and usage patterns

### AI Integration
- `chat_with_graph.py`: Flask API for AI-powered graph querying
- `chat_agent.py`: Implementation of the AI agent for graph interaction
- `example_chat.py`: Example usage of the chat functionality

### Configuration
- `example.env`: Template for environment variables
- `docs/`: Additional documentation and examples
- `training.zip`: Zip containing MD files for training the AI agent

## Technologies and Concepts Used

### Database and Graph Technologies
- **Neo4j**: Graph database for storing and querying relationships
- **NetworkX**: Python library for graph operations
- **Pyvis**: Interactive network visualization

### AI and Machine Learning
- **OpenAI**: Large language model integration
- **OpenAI Agents SDK**: For creating AI agents and function calling
- **LangChain**: Framework for developing LLM applications
  - Chains
  - Document loaders
  - Text splitters
- **Model Context Protocol (MCP)**: 
  - Integrated with Tavily Search API as a fallback search mechanism
  - Used when information is not found in Neo4j database
  - Enhances agent's knowledge retrieval capabilities through external search
  - Implemented as an MCP server stream for real-time information augmentation

### Web Technologies
- **Flask**: Web framework for API endpoints
- **Async/Await**: Asynchronous programming
- **REST APIs**: HTTP endpoints for interaction

### Data Processing
- **AST**: Abstract Syntax Tree parsing for Python code
- **PDF Processing**: PDF text and structure extraction
- **Markdown Processing**: MD to structured data conversion

## Setup and Usage Steps

1. **Environment Setup**
   ```bash
   # Clone the repository
   git clone [repository-url]
   cd neo4j-populator

   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configuration**
   ```bash
   # Copy example.env to .env
   cp example.env .env
   
   # Edit .env with your credentials
   # Required:
   # - Neo4j connection details
   # - OpenAI API key
   # - Other service credentials
   ```

3. **Running Data Import**
   Ensure to put in your desried file_name/location in the code.
   ```bash
   # JSON import
   python json-to-graph.py

   # Repository analysis
   python repo-to-graph.py

   # PDF import
   python pdf-to-graph.py
   ```

4. **Starting the Chat API**
   ```bash
   # Start the Flask server
   python chat_with_graph.py
   ```

5. **Visualizing Code**
   - Used to generate a static as well as interactive html representation of the code dependency graph.
   - Ensure to provide the local path of the directory/repository containing the codebase.
   ```bash
   # Generate code visualization
   python code-visualizer.py
   ```

## Additional Information

### Prerequisites
- Python 3.8+
- Neo4j 4.4+
- OpenAI API access
- Required Python packages (see requirements.txt)

### Best Practices
- Use virtual environments
- Keep sensitive credentials in .env file
- Regular database backups
- Monitor API usage

### Common Issues and Solutions
1. **Neo4j Connection**: Ensure correct bolt URI and credentials
2. **Memory Usage**: Large files may require increased memory limits
3. **API Rate Limits**: Implement appropriate delays for API calls

### Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support and Contact
- Create an issue for bugs or feature requests
