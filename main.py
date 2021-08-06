from app.base import create_app


app = create_app()

if __name__ == 'main':
    app.run(debug=True)
    app.logger.info('---------- App is running --------')
    
    

