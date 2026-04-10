import requests
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views import View


class ClassifyNameView(View):

    def get(self, request):
        name = request.GET.get("name", None)

        # 400: missing or empty
        if name is None or name == "":
            return JsonResponse(
                {"status": "error", "message": "Missing or empty name parameter"},
                status=400,
            )

        # 422: not a string
        if not isinstance(name, str):
            return JsonResponse(
                {"status": "error", "message": "name must be a string"},
                status=422,
            )

        # Call Genderize API
        try:
            response = requests.get(
                "https://api.genderize.io",
                params={"name": name},
                timeout=4,
            )
        except requests.exceptions.Timeout:
            return JsonResponse(
                {"status": "error", "message": "Upstream API timed out"},
                status=502,
            )
        except requests.exceptions.RequestException as e:
            return JsonResponse(
                {"status": "error", "message": f"Upstream API error: {str(e)}"},
                status=502,
            )

        if response.status_code != 200:
            return JsonResponse(
                {"status": "error", "message": "Upstream API returned an error"},
                status=502,
            )

        try:
            payload = response.json()
        except ValueError:
            return JsonResponse(
                {"status": "error", "message": "Invalid response from upstream API"},
                status=502,
            )

        gender = payload.get("gender")
        count = payload.get("count", 0)

        # Edge case: no prediction available
        if gender is None or count == 0:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "No prediction available for the provided name",
                },
                status=200,
            )

        probability = payload.get("probability", 0)
        sample_size = count
        is_confident = bool(probability >= 0.7 and sample_size >= 100)
        processed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return JsonResponse(
            {
                "status": "success",
                "data": {
                    "name": payload.get("name", name).lower(),
                    "gender": gender,
                    "probability": probability,
                    "sample_size": sample_size,
                    "is_confident": is_confident,
                    "processed_at": processed_at,
                },
            },
            status=200,
        )