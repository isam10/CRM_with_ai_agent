# SmartCRM Assistant

An advanced Customer Relationship Management (CRM) system with AI-powered features, built with Django and modern web technologies.

## 🚀 Features

### Core CRM Features
- **Customer Management**: Comprehensive customer database with contact information
- **Sales Tracking**: Monitor sales performance and revenue analytics
- **AI-Powered Chatbot**: Intelligent customer service assistant
- **Churn Prediction**: Machine learning-based customer churn analysis
- **Sales Reporting**: Automated sales summary generation with PDF export

### Enhanced Features (New!)
- **Customer Segmentation**: Advanced customer categorization based on behavior and demographics
- **Task Management**: Comprehensive task tracking and assignment system
- **Marketing Campaigns**: Targeted marketing campaign management with automated delivery
- **Enhanced Analytics**: Interactive dashboards with real-time insights
- **Real-time Updates**: WebSocket-based live updates for collaborative work

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Real-time**: Django Channels, Redis
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **Task Queue**: Celery
- **Charts**: Chart.js
- **PDF Generation**: ReportLab

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd enhanced-smartcrm
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database setup**
   ```bash
   cd crm
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 🎯 Key Enhancements

### 1. Customer Segmentation
- Create dynamic customer segments based on purchase behavior
- Automatic customer assignment to segments
- Visual segment analytics and insights

### 2. Task Management System
- Create, assign, and track customer-related tasks
- Priority levels and due date management
- Real-time status updates
- Task completion analytics

### 3. Marketing Campaigns
- Target specific customer segments
- Automated message delivery simulation
- Campaign performance tracking
- Delivery status monitoring

### 4. Enhanced Analytics Dashboard
- Interactive charts and visualizations
- Real-time metrics and KPIs
- Customer segment distribution analysis
- Task completion rates
- Campaign performance metrics

## 📊 Usage

### Customer Segmentation
1. Navigate to "Segments" in the main menu
2. Click "Create New Segment"
3. Define segment criteria (purchase recency, minimum amount)
4. Customers are automatically assigned based on criteria

### Task Management
1. Go to "Tasks" dashboard
2. Create new tasks with customer assignments
3. Set priorities and due dates
4. Track progress with real-time status updates

### Marketing Campaigns
1. Access "Campaigns" section
2. Create targeted campaigns for specific segments
3. Design message templates
4. Send campaigns and monitor delivery status

### Analytics
1. Visit the "Analytics" dashboard
2. View real-time metrics and charts
3. Analyze customer segment distribution
4. Monitor task completion rates and campaign performance

## 🔧 Configuration

### Redis Setup (for real-time features)
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server
```

### Celery Setup (for background tasks)
```bash
# Start Celery worker
celery -A crm worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A crm beat --loglevel=info
```

## 🚀 Deployment

### Production Settings
1. Update `settings.py` for production
2. Configure PostgreSQL database
3. Set up static file serving
4. Configure Redis for production
5. Use Gunicorn as WSGI server

### Docker Deployment (Optional)
```bash
# Build Docker image
docker build -t enhanced-smartcrm .

# Run container
docker run -p 8000:8000 enhanced-smartcrm
```

## 📈 Performance Features

- **Optimized Queries**: Efficient database queries with select_related and prefetch_related
- **Pagination**: Large datasets handled with Django pagination
- **Caching**: Redis-based caching for improved performance
- **Async Support**: Django Channels for real-time features
- **Background Tasks**: Celery for heavy computations

## 🔒 Security Features

- CSRF protection enabled
- SQL injection prevention
- XSS protection
- Secure session management
- Input validation and sanitization

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 API Documentation

The system includes RESTful API endpoints for:
- Customer management
- Task operations
- Campaign management
- Analytics data
- Real-time updates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🎉 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the UI components
- Chart.js for visualization capabilities
- All contributors and testers

---

**Enhanced SmartCRM Assistant** - Taking customer relationship management to the next level with AI and modern web technologies.

