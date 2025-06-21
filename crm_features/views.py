from django.shortcuts import render, redirect # type: ignore
from django.contrib.auth.models import auth # type: ignore
from django.contrib import messages # type: ignore
from django.http import JsonResponse
from .models import Chatroom
from .ai.report_generation import process_sales_analysis
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings  
from django.http import FileResponse, HttpResponseNotFound ,HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from markdownify import markdownify
from .ai.churnpredict import predictions
import os
import json 

# Create your views here.

def home(request):
    return render(request,'home.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')  
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')  


def logout(request):
    auth.logout(request)
    return redirect('/')


def chatquery(request):
    return render(request,'chatquery.html')


def get_user_room(request):
    user_id=request.session.session_key or request.user.id
    room,_=Chatroom.objects.get_or_create(room_name=f"user_{user_id}")
    return JsonResponse({"room_name":room.room_name})




@csrf_exempt
def sales_summariser(request):
    if request.method == "POST":
        response = process_sales_analysis()
        cleaned_content = response.strip('```json\n').strip("```")

        try:
            data = json.loads(cleaned_content)
        except json.JSONDecodeError:
            return render(request, "sales_summary.html", {
                "error": "Invalid JSON response",
                "displayGraph": False
            })

        json_data = data["json_data"]
        summary = markdownify(data["summary"])


        weekly_sales_data = {
            "type": "bar",
            "data": {
                "labels": list(json_data["weekly_sales_trends"]["sales_by_category"].keys()),
                "datasets": [{
                    "label": "Weekly Sales",
                    "data": list(json_data["weekly_sales_trends"]["sales_by_category"].values()),
                    "backgroundColor": "#4e73df"
                }]
            }
        }

        monthly_sales_data = {
            "type": "bar",
            "data": {
                "labels": list(json_data["monthly_sales_trends"]["sales_by_category"].keys()),
                "datasets": [{
                    "label": "Monthly Sales",
                    "data": list(json_data["monthly_sales_trends"]["sales_by_category"].values()),
                    "backgroundColor": "#1cc88a"
                }]
            }
        }

        yearly_sales_data = {
            "type": "bar",
            "data": {
                "labels": list(json_data["yearly_sales_trends"]["sales_by_category"].keys()),
                "datasets": [{
                    "label": "Yearly Sales",
                    "data": list(json_data["yearly_sales_trends"]["sales_by_category"].values()),
                    "backgroundColor": "#36b9cc"
                }]
            }
        }

        region_sales_data = {
            "type": "pie",
            "data": {
                "labels": list(json_data["yearly_sales_trends"]["sales_by_region"].keys()),
                "datasets": [{
                    "label": "Sales by Region",
                    "data": list(json_data["yearly_sales_trends"]["sales_by_region"].values()),
                    "backgroundColor": [
                        "#f6c23e", "#e74a3b", "#858796", "#1cc88a"
                    ]
                }]
            }
        }

        context = {
            "summary": summary,
            "displayGraph": True,
            "weekly_sales_data": json.dumps(weekly_sales_data),
            "monthly_sales_data": json.dumps(monthly_sales_data),
            "yearly_sales_data": json.dumps(yearly_sales_data),
            "region_sales_data": json.dumps(region_sales_data)
        }

        file_path = os.path.join(settings.MEDIA_ROOT, 'sales_report.pdf')
        generate_pdf(summary, file_path)

        return render(request, "sales_summary.html", context)

    return render(request, "sales_summary.html", {"displayGraph": False})

def download_pdf(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'sales_report.pdf')
    
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    return HttpResponseNotFound('PDF not found yet. Please generate it first.')

def generate_pdf(report_data, filename):
    """Generate PDF using ReportLab"""
  
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    
    title = Paragraph("Sales Analysis Report", styles['Title'])
    content.append(title)
    content.append(Spacer(1, 12))
    
    if isinstance(report_data, dict):
        text = report_data.get('summary', 'No analysis available')
    else:
        text = str(report_data)
        
    body = Paragraph(text, styles['BodyText'])
    content.append(body)
    
    doc.build(content)


@csrf_exempt
def run_churn_prediction(request):
    if request.method == "POST":
        try:
            result = predictions()  # Call the function that returns the churn prediction data
            return render(request, "churn_results.html", {"notifications": result})
        except Exception as e:
            return render(request, "churn_results.html", {"error": f"Error: {str(e)}"})
    return render(request, "churn_results.html")

# def run_churn_prediction(request):
#     if request.method == 'POST':
#         try:
#             results = predictions()  # your Celery task or function call
#             return JsonResponse({"status": "success", "data": results})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)
#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
# Enhanced CRM Views

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import CustomerSegment, CustomerSegmentMembership, Task, MarketingCampaign, CampaignDelivery
import datetime
from django.utils import timezone

def customer_segments(request):
    """View to display and manage customer segments"""
    segments = CustomerSegment.objects.annotate(
        customer_count=Count('customersegmentmembership')
    ).order_by('-created_at')
    
    return render(request, 'customer_segments.html', {'segments': segments})

def create_segment(request):
    """View to create a new customer segment"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        # Simple criteria for demo - customers who made purchases in last 30 days
        criteria = {
            'purchase_recency': 30,
            'min_purchase_amount': float(request.POST.get('min_amount', 0))
        }
        
        segment = CustomerSegment.objects.create(
            name=name,
            description=description,
            criteria=criteria
        )
        
        # Auto-assign customers based on criteria
        assign_customers_to_segment(segment)
        
        messages.success(request, f'Segment "{name}" created successfully!')
        return redirect('customer_segments')
    
    return render(request, 'create_segment.html')

def assign_customers_to_segment(segment):
    """Automatically assign customers to a segment based on criteria"""
    criteria = segment.criteria
    
    # Example logic: customers with recent purchases
    recent_date = timezone.now() - datetime.timedelta(days=criteria.get('purchase_recency', 30))
    min_amount = criteria.get('min_purchase_amount', 0)
    
    # Find customers matching criteria
    matching_customers = Customer.objects.filter(
        sale__sale_date__gte=recent_date,
        sale__amount__gte=min_amount
    ).distinct()
    
    # Create memberships
    for customer in matching_customers:
        CustomerSegmentMembership.objects.get_or_create(
            customer=customer,
            segment=segment
        )

def tasks_dashboard(request):
    """View to display task management dashboard"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    tasks = Task.objects.all()
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    task_stats = {
        'total': Task.objects.count(),
        'pending': Task.objects.filter(status='pending').count(),
        'in_progress': Task.objects.filter(status='in_progress').count(),
        'completed': Task.objects.filter(status='completed').count(),
        'overdue': Task.objects.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
    }
    
    context = {
        'page_obj': page_obj,
        'task_stats': task_stats,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Task.TASK_STATUS_CHOICES,
        'priority_choices': Task.TASK_PRIORITY_CHOICES,
    }
    
    return render(request, 'tasks_dashboard.html', context)

def create_task(request):
    """View to create a new task"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        customer_id = request.POST.get('customer_id')
        assigned_to = request.POST.get('assigned_to')
        priority = request.POST.get('priority', 'medium')
        due_date_str = request.POST.get('due_date')
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
                due_date = timezone.make_aware(due_date)
            except ValueError:
                pass
        
        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(customer_id=customer_id)
            except Customer.DoesNotExist:
                pass
        
        Task.objects.create(
            title=title,
            description=description,
            customer=customer,
            assigned_to=assigned_to,
            priority=priority,
            due_date=due_date
        )
        
        messages.success(request, 'Task created successfully!')
        return redirect('tasks_dashboard')
    
    customers = Customer.objects.all()
    return render(request, 'create_task.html', {'customers': customers})

def update_task_status(request, task_id):
    """AJAX view to update task status"""
    if request.method == 'POST':
        task = get_object_or_404(Task, task_id=task_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Task.TASK_STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            
            return JsonResponse({'success': True, 'message': 'Task status updated'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def marketing_campaigns(request):
    """View to display marketing campaigns"""
    campaigns = MarketingCampaign.objects.select_related('target_segment').order_by('-created_at')
    return render(request, 'marketing_campaigns.html', {'campaigns': campaigns})

def create_campaign(request):
    """View to create a new marketing campaign"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        segment_id = request.POST.get('segment_id')
        message_template = request.POST.get('message_template')
        
        try:
            segment = CustomerSegment.objects.get(segment_id=segment_id)
            
            campaign = MarketingCampaign.objects.create(
                name=name,
                description=description,
                target_segment=segment,
                message_template=message_template
            )
            
            messages.success(request, f'Campaign "{name}" created successfully!')
            return redirect('marketing_campaigns')
            
        except CustomerSegment.DoesNotExist:
            messages.error(request, 'Selected segment does not exist.')
    
    segments = CustomerSegment.objects.all()
    return render(request, 'create_campaign.html', {'segments': segments})

@csrf_exempt
def send_campaign(request, campaign_id):
    """View to send a marketing campaign"""
    if request.method == 'POST':
        campaign = get_object_or_404(MarketingCampaign, campaign_id=campaign_id)
        
        if campaign.status != 'draft':
            return JsonResponse({'success': False, 'message': 'Campaign already sent or not in draft status'})
        
        # Get customers in the target segment
        customers = Customer.objects.filter(
            customersegmentmembership__segment=campaign.target_segment
        ).distinct()
        
        # Create delivery records (simulate sending)
        delivery_count = 0
        for customer in customers:
            CampaignDelivery.objects.create(
                campaign=campaign,
                customer=customer,
                status='sent',
                sent_at=timezone.now()
            )
            delivery_count += 1
        
        # Update campaign status
        campaign.status = 'completed'
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Campaign sent to {delivery_count} customers'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def enhanced_analytics(request):
    """Enhanced analytics dashboard"""
    # Customer segmentation analytics
    segment_stats = CustomerSegment.objects.annotate(
        customer_count=Count('customersegmentmembership')
    ).values('name', 'customer_count')
    
    # Task completion analytics
    task_completion_rate = Task.objects.filter(status='completed').count() / max(Task.objects.count(), 1) * 100
    
    # Campaign performance
    campaign_stats = MarketingCampaign.objects.annotate(
        delivery_count=Count('campaigndelivery')
    ).values('name', 'delivery_count', 'status')
    
    # Recent activity
    recent_tasks = Task.objects.order_by('-created_at')[:5]
    recent_campaigns = MarketingCampaign.objects.order_by('-created_at')[:5]
    
    context = {
        'segment_stats': list(segment_stats),
        'task_completion_rate': round(task_completion_rate, 2),
        'campaign_stats': list(campaign_stats),
        'recent_tasks': recent_tasks,
        'recent_campaigns': recent_campaigns,
    }
    
    return render(request, 'enhanced_analytics.html', context)

