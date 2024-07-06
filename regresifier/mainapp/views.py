from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import json

MAX_FILE_SIZE = 5 * 1024 * 1024

@csrf_exempt
def upload_csv(request):
    print("Request method:", request.method)
    if request.method == "OPTIONS":
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return JsonResponse({'error': 'File is not a CSV'}, status=400)
        if file.size > MAX_FILE_SIZE:
            return JsonResponse({'error': f'File is too large. Max size is {MAX_FILE_SIZE / (1024 * 1024)} MB'}, status=400)
        
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)
        
        try:
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
            
            # Store file path in session
            request.session['csv_file_path'] = file_path
            request.session.save()  # Explicitly save the session
            
            response = JsonResponse({'columns': columns})
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Credentials"] = "true"
            response.set_cookie('sessionid', request.session.session_key)  # Explicitly set the session cookie
            print("Session ID set:", request.session.session_key)
            return response
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def run_linear_regression(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        x_columns = data.get('x_columns', [])
        y_column = data.get('y_column')
        if not x_columns or not y_column:
            return JsonResponse({'error': 'Missing X or Y columns'}, status=400)
        
        file_path = request.session.get('csv_file_path')
        print("File path from session:", file_path)
        if not file_path:
            return JsonResponse({'error': 'No CSV file found. Please upload a file first.'}, status=400)
        
        try:
            df = pd.read_csv(file_path)
            X = df[x_columns]
            y = df[y_column]
            
            model = LinearRegression()
            model.fit(X, y)
            
            coefficients = dict(zip(x_columns, model.coef_))
            intercept = model.intercept_
            
            equation = f"y = {intercept:.4f}"
            for col, coef in coefficients.items():
                equation += f" + {coef:.4f} * {col}"
            
            return JsonResponse({
                'equation': equation,
                'coefficients': coefficients,
                'intercept': intercept
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def index(request):
    return render(request, 'index.html')
