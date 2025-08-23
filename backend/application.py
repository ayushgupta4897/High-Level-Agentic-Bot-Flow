"""AWS Beanstalk application entry point"""

from app.main import app

# AWS Beanstalk expects an 'application' variable
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
