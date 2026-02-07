# AI-Native Todo Application

## Overview

This is a full-stack AI-powered todo application featuring:
- Frontend: Next.js application
- Backend: FastAPI application
- Database: Neon PostgreSQL
- AI Chatbot: Natural language task management

The application allows users to register accounts, log in securely, and manage their personal tasks. The system enforces data isolation so users can only access their own tasks. The application features a modern UI with responsive design, advanced task management capabilities, comprehensive security measures, and an AI-powered chatbot for natural language task management.

## Kubernetes Deployment

The application can be deployed to Kubernetes using the provided Helm chart.

### Prerequisites
- Docker
- Kubernetes cluster (Minikube for local development)
- Helm 3+

### Local Development with Minikube

1. Start Minikube:
   ```bash
   minikube start --memory=4096 --cpus=2
   ```

2. Set Docker environment:
   ```bash
   eval $(minikube docker-env)
   ```

3. Build Docker images:
   ```bash
   # Build frontend
   docker build -t todo-frontend:latest -f ./frontend/Dockerfile ./frontend

   # Build backend
   docker build -t todo-backend:latest -f ./backend/Dockerfile ./backend
   ```

4. Install the Helm chart:
   ```bash
   cd helm/todo-chart
   helm install todo-app .
   ```

5. Access the application:
   ```bash
   minikube service todo-app-frontend --url
   ```

For detailed deployment instructions, see [docs/infrastructure/deployment-guide.md](docs/infrastructure/deployment-guide.md).

### Configuration
Sensitive configuration values (database URLs, API keys) should be provided as secrets during Helm installation. See the Helm documentation for details.

## Architecture

- **Frontend**: Next.js (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python 3.11
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: JWT-based authentication with secure token handling
- **AI/Chatbot**: Natural Language Processing with intent recognition and task management
- **Containerization**: Docker and Docker Compose for deployment
- **Testing**: Unit, Integration, Functional, and E2E testing frameworks

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── ai/                     # AI and chatbot components
│   │   │   ├── backend_integration.py
│   │   │   ├── chatbot_orchestrator.py
│   │   │   ├── nlp_intent_processor.py
│   │   │   ├── quality_guard.py
│   │   │   ├── response_composer.py
│   │   │   └── task_control.py
│   │   ├── api/
│   │   │   ├── chat_router.py      # AI chatbot endpoints
│   │   │   └── ...                 # Other API routers
│   │   ├── middleware/
│   │   │   ├── chat_auth.py        # Chat authentication
│   │   │   └── ...                 # Other middleware
│   │   ├── models/
│   │   │   ├── chat.py             # Chat models
│   │   │   └── chat_models.py      # Additional chat models
│   │   ├── services/
│   │   │   ├── chat_service.py     # Chat service logic
│   │   │   └── ...                 # Other services
│   │   └── utils/
│   ├── requirements.txt
│   ├── alembic/
│   ├── docker-compose.yml
│   └── Dockerfile.backend
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── components/
│   │   │   │   └── Common/         # Shared components
│   │   │   ├── pages/
│   │   │   ├── context/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   ├── components/
│   │   └── ...
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile.frontend
├── docker-config/                  # Docker configuration files
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── documentation/                  # Comprehensive documentation
│   ├── API_DOCUMENTATION.md
│   ├── AUTH_INTEGRATION.md
│   ├── BACKUP_RECOVERY_PROCEDURES.md
│   ├── DEPLOYMENT_DOCUMENTATION.md
│   ├── ENVIRONMENT_SETUP.md
│   ├── FINAL_INTEGRATION_TESTING.md
│   └── SECURITY_REVIEW_PENTEST.md
├── specs/                          # Specification documents
│   ├── 1-ai-todo-chatbot/          # AI chatbot specifications
│   │   ├── spec.md
│   │   ├── plan.md
│   │   ├── tasks.md
│   │   └── ...
│   └── 1-phase2-todo-app/          # Main app specifications
├── tests/                          # Testing suite
│   ├── unit/
│   ├── integration/
│   ├── functional/
│   └── e2e/
├── .specify/                       # Spec-driven development tools
│   ├── memory/
│   ├── scripts/
│   └── templates/
├── .claude/                        # Claude Code agents
│   └── agents/
├── .env
└── README.md
```

## Setup

### Backend Setup

1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env` file
4. Initialize the database: `alembic upgrade head`
5. Start the server: `uvicorn src.main:app --reload`

### Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Configure environment variables in `.env` file as needed
4. Start the development server: `npm run dev`

### Docker Setup (Recommended for Production)

1. Navigate to the project root: `cd ..`
2. Build and start services: `docker-compose -f docker-config/docker-compose.yml up --build`
3. Or for development: `docker-compose -f docker-config/docker-compose.dev.yml up`

### Docker Compose Setup (Simplified)

Alternatively, you can use the simplified docker-compose.yml file in the project root:

1. Navigate to the project root: `cd ..`
2. Build and start services: `docker-compose up --build`
3. Access the application at `http://localhost:3000`

The application consists of two main services:
- **Backend**: FastAPI application running on port 8000
- **Frontend**: Next.js application running on port 3000

Both services are configured with automatic restart and data persistence.

### Environment Setup Documentation

For detailed environment setup instructions, refer to `documentation/ENVIRONMENT_SETUP.md`.

## Features

### User Management
- User registration with email validation
- Secure login/logout functionality
- JWT-based session management
- User data isolation and privacy

### Task Management
- **Create Tasks**: Add new tasks with title, description, priority, due date, category, and recurrence options
- **Read Tasks**: View all tasks with filtering and sorting capabilities
- **Update Tasks**: Modify task details including title, description, completion status, priority, etc.
- **Delete Tasks**: Remove tasks with confirmation modal
- **Mark Complete/Incomplete**: Toggle task completion status

### Advanced Task Features
- **Task Properties**:
  - Title (automatically capitalizes first letter)
  - Description (optional)
  - Priority levels: Low, Medium, High
  - Due dates with calendar picker
  - Categories: Work, Home, Other
  - Recurrence options: None, Daily, Weekly, Monthly
- **Smart Filtering**: Filter by all, active, completed, overdue, or upcoming tasks
- **Advanced Sorting**: Sort by creation date, due date, priority, or title
- **Search Functionality**: Search through task titles and descriptions

### AI-Powered Chatbot Features
- **Natural Language Processing**: Intuitive task management through conversational interface
- **Intent Recognition**: Smart parsing of user commands to create, update, or manage tasks
- **Chat Orchestration**: Sophisticated dialogue management and response composition
- **Quality Guard**: AI response validation and safety checks
- **Task Control**: Seamless integration between chat commands and task operations
- **User Context Handling**: Personalized responses based on user data and preferences

### Dashboard & Analytics
- **Task Statistics**: Real-time counters for total, completed, and pending tasks
- **Quick Actions**: Direct links to view tasks or create new ones
- **Recent Activity Feed**: Track task-related activities (creation, updates, completion, deletion)

### User Interface
- **Modern Design**: Purple-to-pink gradient theme with clean, contemporary UI
- **Responsive Layout**: Fully responsive design that works on mobile, tablet, and desktop
- **Intuitive Navigation**: Easy-to-use navigation with consistent layout across pages
- **Loading States**: Visual feedback during API calls and data loading
- **Error Handling**: Clear error messages and validation feedback

### Security Features
- Passwords are securely hashed using bcrypt
- JWT tokens with proper expiration times
- Input validation and sanitization (XSS protection)
- Data isolation - users can only access their own tasks
- Protection against common web vulnerabilities
- Secure API endpoints with proper authentication checks
- AI response validation and safety mechanisms

### Technical Features
- **API Layer**: Centralized API client using native fetch
- **State Management**: Context API for authentication and loading states
- **Type Safety**: Full TypeScript support with type definitions
- **Component Architecture**: Reusable, modular components
- **Real-time Updates**: Event-driven updates across components
- **Activity Tracking**: Comprehensive logging of user actions
- **Containerization**: Docker support for consistent deployments
- **Testing Frameworks**: Unit, integration, functional, and E2E testing coverage

## Environment Variables

### Frontend (.env)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL (default: https://rimshaarshad-todo-app.hf.space)
- `NEXT_PUBLIC_APP_URL`: Frontend application URL

### Backend (.env)
- `DATABASE_URL`: PostgreSQL database connection string
- `SECRET_KEY`: JWT secret key for token signing
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Tasks
- `GET /tasks` - Get all user tasks
- `POST /tasks` - Create a new task
- `GET /tasks/{id}` - Get a specific task
- `PUT /tasks/{id}` - Update a task
- `DELETE /tasks/{id}` - Delete a task

### Chat/AI
- `POST /chat/process` - Process natural language input and manage tasks
- `GET /chat/history/{user_id}` - Get chat history for a specific user
- `POST /chat/message` - Send a message to the chatbot
- `DELETE /chat/clear/{user_id}` - Clear chat history for a user

### Activities
- `GET /activities` - Get user activity logs
- `POST /activities` - Log a new activity

### Health
- `GET /health` - Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Testing

The application includes comprehensive test suites across multiple layers:
- **Unit Tests**: Located in `tests/unit/` - testing individual components and functions
- **Integration Tests**: Located in `tests/integration/` - testing component interactions
- **Functional Tests**: Located in `tests/functional/` - testing complete feature workflows
- **End-to-End Tests**: Located in `tests/e2e/` - testing user journeys across the entire application

Run tests using the provided test scripts in each respective directory or refer to `documentation/FINAL_INTEGRATION_TESTING.md` for detailed testing procedures.

## Documentation

Comprehensive documentation is available in the `documentation/` directory:
- `API_DOCUMENTATION.md` - Complete API reference
- `AUTH_INTEGRATION.md` - Authentication integration guide
- `BACKUP_RECOVERY_PROCEDURES.md` - Backup and recovery procedures
- `DEPLOYMENT_DOCUMENTATION.md` - Deployment guidelines
- `ENVIRONMENT_SETUP.md` - Environment setup instructions
- `FINAL_INTEGRATION_TESTING.md` - Integration testing procedures
- `SECURITY_REVIEW_PENTEST.md` - Security review and penetration testing

## Deployment

For production deployment, follow these steps or refer to `documentation/DEPLOYMENT_DOCUMENTATION.md`:
1. Set up environment variables for production
2. Build the frontend: `npm run build`
3. Deploy the backend with proper security configurations
4. Configure reverse proxy and SSL certificates
5. Set up database backups and monitoring
6. Use Docker Compose for containerized deployment: `docker-compose -f docker-config/docker-compose.yml up -d`

## Specifications

Detailed specifications are available in the `specs/` directory:
- `specs/1-ai-todo-chatbot/` - AI chatbot feature specifications
- `specs/1-phase2-todo-app/` - Main application specifications

## AI Agents

The application uses specialized AI agents for various functions, documented in `.claude/agents/`:
- `chatbot-orchestrator.md` - Manages the chatbot conversation flow
- `nlp-intent-agent.md` - Handles natural language processing and intent recognition
- `ai-response-composer.md` - Composes human-friendly responses
- `ai-quality-guard.md` - Ensures AI response quality and safety
- And more specialized agents for different aspects of the system

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# Kubernetes-Deployment
