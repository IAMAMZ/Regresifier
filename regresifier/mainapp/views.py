from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
import pandas as pd

# Define the maximum file size (e.g., 5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']

        # Check if the file is a CSV
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not a CSV'}, status=400)

        # Check if the file size is within the limit
        if file.size > MAX_FILE_SIZE:
            return JsonResponse({'error': f'File is too large. Max size is {MAX_FILE_SIZE / (1024 * 1024)} MB'}, status=400)

        # Save the file
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        # Read the CSV file using pandas
        file_path = fs.path(filename)
        try:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'file_url': file_url, 'columns': columns})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def index(request):
    return HttpResponse("Hello, world.")
