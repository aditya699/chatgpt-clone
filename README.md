# FastAPI Chat Backend Groundwork

A foundational backend implementation using FastAPI for a chat application. This project provides the basic infrastructure and authentication system necessary for building more complex chat-based applications.

## Features

### Core Infrastructure
- FastAPI framework setup with proper routing
- Azure AD Authentication integration
- Session management
- CORS configuration

### User Management
- Azure AD user authentication
- User session handling
- Last login tracking
- User profile storage in MongoDB

### Chat System Basics
- Chat session creation
- Message storage and retrieval
- Pagination for chat history
- Basic message echoing (placeholder for future AI integration)

## Project Structure
```
chatgpt-clone/
├── app/
│   ├── auth/
│   │   ├── route.py      # Authentication routes
│   │   └── utils.py      # Auth utilities
│   ├── chat/
│   │   └── routes.py     # Chat handling routes
│   └── training/         # Future training module
├── main.py              # Application entry point
└── requirements.txt
```

## Prerequisites
- Python 3.8+
- MongoDB
- Azure AD Account (for authentication)

## Environment Variables
```
CLIENT_ID=your_azure_client_id
TENANT_ID=your_azure_tenant_id
CLIENT_SECRET=your_azure_client_secret
REDIRECT_URI=your_redirect_uri
MONGO_CON=your_mongodb_connection_string
SECRET_KEY=your_secret_key
```

## Key Endpoints

### Authentication
- `GET /auth/login` - Redirect to Azure AD login
- `GET /auth/callback` - Handle OAuth callback

### Chat
- `POST /chat/create-session` - Create new chat session
- `GET /chat/get-user-sessions` - Get user's chat history
- `POST /chat/message` - Send message in a session

## Setup
1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables
5. Run the application: `uvicorn main:app --reload`

## Future Scope
This groundwork is designed to be extended with:
- AI model integration
- File handling
- Image processing
- Advanced chat features
- Analytics and monitoring

## Note
This is a foundation project focused on establishing proper backend architecture. It provides the groundwork for building more complex features on top of a solid base.