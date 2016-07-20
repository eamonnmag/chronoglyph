from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse
# Create your views here.
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from ChronoGlyph_Web.models import TimeSeriesCollection, TimeSeriesModel
from ChronoGlyph_Web.timeseries_analysis.analysis_engine import AnalysisEngine
import json


def get_collection_by_id(collection_id):
    collection = TimeSeriesCollection.objects.filter(collection_id=collection_id)

    if len(collection) > 0:
        return collection.__getitem__(0)
    return None


def datasets(request):
    return render_to_response("templates/datasets.html", {},
                              context_instance=RequestContext(request))

def get_compressed(request):
    return render_to_response("templates/compress.html", {},
                              context_instance=RequestContext(request))


def analytics(request):
    collection_id = request.GET.get('collection', '')

    analyses = []
    if collection_id is not '':
        collection = get_collection_by_id(collection_id)
        print collection.name
        if collection is not None:
            analyses = TimeSeriesModel.objects.filter(time_series_collection=collection).order_by('-created')

    data_collections = TimeSeriesCollection.objects.all()
    latest_analysis = []
    if len(analyses) > 0:
        latest_analysis = analyses.__getitem__(0)

    return render_to_response("templates/analytics.html", {"current_collection": collection_id, "analyses": analyses,
                                                           "collections": data_collections,
                                                           "latest_analysis": latest_analysis},
                              context_instance=RequestContext(request))


@csrf_exempt
def create_analysis(request):
    collection_id = request.POST.get('collection')

    model_name = request.POST.get('model_name')
    alphabet_size = request.POST.get('alphabet', 4)
    window_size = request.POST.get('window_size', 6)
    cutoff = request.POST.get('cutoff', 6)
    algorithm = request.POST.get('algorithm', 'bound_sliding_window')
    sw_segment_size = request.POST.get('algorithm_parameter', 6)
    if sw_segment_size == '':
        sw_segment_size = 6

    collection = get_collection_by_id(collection_id)

    analysis_model = TimeSeriesModel(model_name=model_name, window_size=window_size, alphabet_size=alphabet_size,
                                     cutoff=cutoff, algorithm=algorithm, algorithm_parameter=sw_segment_size,
                                     time_series_collection=collection)

    analysis_model.save()
    ae = AnalysisEngine()
    ae.run_analysis(analysis_model)

    return redirect('/?collection=' + collection_id)


def delete_analysis(request, model_name):
    models = TimeSeriesModel.objects.filter(model_name=model_name)
    for model in models:
        model.delete()

    return HttpResponse(json.dumps({"status": "delete ok", "name": model_name}), content_type='application/json')


def get_analysis_file(request):
    model_name = request.GET.get('model_name')
    file_type = request.GET.get('file_type')

    data = {"error": "The file type you requested does not exist!"}

    ts = TimeSeriesModel.objects.filter(model_name=model_name)
    if len(ts) > 0:
        ts = ts.__getitem__(0)

        if file_type == 'parallel_coords':
            data = open(ts.parallel_coords_file).read()  # opens the json file and saves the raw contents
        elif file_type == 'time_series':
            data = open(ts.time_series_file).read()
        elif file_type == 'network':
            data = open(ts.network_file).read()

    data = json.loads(data)
    return HttpResponse(json.dumps(data), content_type='application/json')



