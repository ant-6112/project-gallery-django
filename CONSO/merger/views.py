import os
from django.shortcuts import render
from .forms import MergeRequestForm
from .models import MergeRequest
from openpyxl import load_workbook

def home(request):
    return render(request, 'merger/index.html')

def merge_excel(request):
    if request.method == 'POST':
        form = MergeRequestForm(request.POST, request.FILES)
        if form.is_valid():
            merge_request = form.save()
            file1 = merge_request.file1.path
            file2 = merge_request.file2.path

            workbook1 = load_workbook(filename=file1)
            workbook2 = load_workbook(filename=file2)

            worksheet1 = workbook1.active
            worksheet2 = workbook2.active

            merged_workbook = load_workbook(filename=file1)
            merged_worksheet = merged_workbook.active

            for row in worksheet2.iter_rows():
                merged_worksheet.append([cell.value for cell in row])

            output_path = os.path.join(os.path.dirname(file1), 'merged.xlsx')
            merged_workbook.save(output_path)

            os.remove(file1)
            os.remove(file2)

            context = {
                'form': form,
                'output_path': output_path,
            }
            return render(request, 'merger/merge_success.html', context)
    else:
        form = MergeRequestForm()

    return render(request, 'merger/merge_form.html', {'form': form})