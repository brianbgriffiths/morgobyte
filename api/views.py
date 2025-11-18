from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from .yoto_client import YotoAPIClient
import requests
import json


def get_client_from_request(request):
    """Get YotoAPIClient configured with credentials from request headers or environment."""
    print("=== get_client_from_request called ===")
    print(f"All request headers: {dict(request.headers)}")
    
    client = YotoAPIClient()
    
    # Get user's tokens from headers (stored in their browser's IndexedDB)
    access_token = request.headers.get('X-Access-Token')
    refresh_token = request.headers.get('X-Refresh-Token')
    client_id = request.headers.get('X-Client-Id')
    client_secret = request.headers.get('X-Client-Secret')
    
    print(f"Headers received:")
    print(f"  X-Access-Token: {'present' if access_token else 'missing'}")
    print(f"  X-Refresh-Token: {'present' if refresh_token else 'missing'}")
    print(f"  X-Client-Id: {'present' if client_id else 'missing'}")
    print(f"  X-Client-Secret: {'present' if client_secret else 'missing'}")
    
    # If USE_ENV_CREDENTIALS is enabled, use server-side CLIENT credentials from settings
    # but still use user's tokens from headers
    if settings.USE_ENV_CREDENTIALS:
        print("Using environment CLIENT credentials from settings")
        client.client_id = settings.YOTO_CLIENT_ID
        client.client_secret = settings.YOTO_CLIENT_SECRET
        print(f"Set client_id from env: {'present' if client.client_id else 'missing'}")
        print(f"Set client_secret from env: {'present' if client.client_secret else 'missing'}")
    else:
        # Use client credentials from headers
        if client_id:
            client.client_id = client_id
            print(f"Set client_id: {client_id[:30]}...")
        if client_secret:
            client.client_secret = client_secret
            print(f"Set client_secret: {client_secret[:30]}...")
    
    # Always use user's tokens from headers
    if access_token:
        client.access_token = access_token
        print(f"Set access_token: {access_token[:30]}...")
    if refresh_token:
        client.refresh_token = refresh_token
        print(f"Set refresh_token: {refresh_token[:30]}...")
        
    return client


@require_http_methods(["GET"])
def setup_page(request):
    """Render the setup page."""
    # If USE_ENV_CREDENTIALS is enabled, redirect to main app
    if settings.USE_ENV_CREDENTIALS:
        from django.shortcuts import redirect
        return redirect('/')
    
    # Read the static setup.html file and render it directly
    import os
    from django.http import HttpResponse
    
    setup_file_path = os.path.join(settings.BASE_DIR, 'static', 'setup.html')
    with open(setup_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HttpResponse(content, content_type='text/html')


@require_http_methods(["GET"])
def setup_account_only_page(request):
    """Render the account-only setup page for server deployments."""
    import os
    from django.http import HttpResponse
    
    setup_file_path = os.path.join(settings.BASE_DIR, 'static', 'setup-account.html')
    with open(setup_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HttpResponse(content, content_type='text/html')


@require_http_methods(["GET"])
def app_page(request):
    """Render the main app page."""
    import os
    from django.conf import settings
    from django.http import HttpResponse
    
    app_file_path = os.path.join(settings.BASE_DIR, 'static', 'app.html')
    with open(app_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Inject server config as JavaScript variable
    config_script = f'<script>window.SERVER_CONFIG = {{useEnvCredentials: {"true" if settings.USE_ENV_CREDENTIALS else "false"}}};</script>'
    # Insert before closing </head> tag
    content = content.replace('</head>', config_script + '</head>')
    
    return HttpResponse(content, content_type='text/html')


def service_worker(request):
    """Serve the service worker from root."""
    import os
    from django.conf import settings
    from django.http import HttpResponse
    
    sw_file_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    with open(sw_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return HttpResponse(content, content_type='application/javascript')


@require_http_methods(["GET"])
def check_config(request):
    """Check if server is using environment credentials."""
    use_env = settings.USE_ENV_CREDENTIALS
    print(f"=== check_config called ===")
    print(f"USE_ENV_CREDENTIALS: {use_env}")
    return JsonResponse({
        'status': 'success',
        'useEnvCredentials': use_env
    })


@require_http_methods(["GET"])
def start_oauth(request):
    """Start OAuth flow using server credentials from .env"""
    from django.shortcuts import redirect
    from urllib.parse import urlencode
    
    if not settings.USE_ENV_CREDENTIALS or not settings.YOTO_CLIENT_ID:
        return JsonResponse({
            'status': 'error',
            'message': 'Server credentials not configured'
        }, status=500)
    
    current_host = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    redirect_uri = f"{protocol}://{current_host}/callback"
    
    print(f"=== start_oauth ===")
    print(f"current_host: {current_host}")
    print(f"protocol: {protocol}")
    print(f"redirect_uri: {redirect_uri}")
    print(f"is_secure: {request.is_secure()}")
    
    params = {
        'response_type': 'code',
        'client_id': settings.YOTO_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'scope': 'offline_access library:read players:read family:read',
        'audience': 'https://api.yotoplay.com'
    }
    
    auth_url = f"https://login.yotoplay.com/oauth/authorize?{urlencode(params)}"
    print(f"auth_url: {auth_url}")
    return redirect(auth_url)


@csrf_exempt
@require_http_methods(["POST"])
def exchange_token_account(request):
    """Exchange authorization code for tokens using server credentials."""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        redirect_uri = data.get('redirectUri')

        if not settings.USE_ENV_CREDENTIALS:
            return JsonResponse({
                'status': 'error',
                'message': 'Server credentials not enabled'
            }, status=400)

        if not code or not redirect_uri:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters: code or redirectUri'
            }, status=400)

        # Use credentials from .env
        client_id = settings.YOTO_CLIENT_ID
        client_secret = settings.YOTO_CLIENT_SECRET

        if not client_id or not client_secret:
            return JsonResponse({
                'status': 'error',
                'message': 'Server credentials not configured in .env'
            }, status=500)

        # Exchange code for tokens
        token_url = 'https://login.yotoplay.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': 'https://api.yotoplay.com'
        }

        print(f"Exchanging token with redirect_uri: {redirect_uri}")
        
        token_response = requests.post(token_url, json=token_data)
        
        if not token_response.ok:
            print(f"Token exchange failed: {token_response.status_code} - {token_response.text}")
            return JsonResponse({
                'status': 'error',
                'message': f'Token exchange failed: {token_response.text}'
            }, status=token_response.status_code)

        tokens = token_response.json()
        
        return JsonResponse({
            'status': 'success',
            'data': tokens
        })

    except Exception as e:
        print(f"Token exchange error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def exchange_token(request):
    """Exchange authorization code for access and refresh tokens."""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        client_id = data.get('clientId')
        client_secret = data.get('clientSecret')
        redirect_uri = data.get('redirectUri')

        print(f"Token exchange request: code={code[:20] if code else None}..., client_id={client_id[:20] if client_id else None}..., redirect_uri={redirect_uri}")

        if not all([code, client_id, client_secret, redirect_uri]):
            missing = []
            if not code: missing.append('code')
            if not client_id: missing.append('clientId')
            if not client_secret: missing.append('clientSecret')
            if not redirect_uri: missing.append('redirectUri')
            
            error_msg = f'Missing required parameters: {", ".join(missing)}'
            print(f"ERROR: {error_msg}")
            
            return JsonResponse({
                'status': 'error',
                'message': error_msg
            }, status=400)

        # Exchange code for tokens
        token_url = 'https://login.yotoplay.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret,
            'audience': 'https://api.yotoplay.com'
        }

        print(f"Sending request to {token_url}")
        response = requests.post(token_url, json=token_data)
        print(f"Response status: {response.status_code}")
        
        response.raise_for_status()

        result = response.json()
        print(f"Token exchange successful!")

        return JsonResponse({
            'status': 'success',
            'data': result
        })

    except requests.exceptions.RequestException as e:
        print(f"Token exchange HTTP error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
        return JsonResponse({
            'status': 'error',
            'message': f'Token exchange failed: {str(e)}'
        }, status=500)
    except Exception as e:
        print(f"Token exchange error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def oauth_callback(request):
    """Handle OAuth callback - redirect to setup page with code."""
    from django.shortcuts import redirect
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')

    print(f"=== OAuth Callback View ===")
    print(f"Code: {code[:20] if code else None}...")
    print(f"State: {state[:20] if state else None}...")
    print(f"Error: {error}")
    
    # If using env credentials (server mode), redirect to setup page with code
    if settings.USE_ENV_CREDENTIALS:
        print("Using env credentials - redirecting to /setup/ with code")
        if error:
            return redirect(f'/setup/?error={error}')
        return redirect(f'/setup/?code={code}')
    
    # Otherwise, use popup callback flow for local setup
    print("Rendering oauth_callback.html for popup flow")
    if error:
        return render(request, 'oauth_callback.html', {
            'error': error,
            'error_description': request.GET.get('error_description', 'Authorization failed')
        })

    return render(request, 'oauth_callback.html', {
        'code': code,
        'state': state
    })


@require_http_methods(["GET"])
def test_connection(request):
    """Test the Yoto API connection."""
    try:
        client = YotoAPIClient()
        client.authenticate()
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully connected to Yoto API'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_family(request):
    """Get family information from Yoto API."""
    try:
        client = YotoAPIClient()
        family_data = client.get_family()
        return JsonResponse({
            'status': 'success',
            'data': family_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_players(request):
    """Get list of players from Yoto API."""
    try:
        client = get_client_from_request(request)
        
        if not client.access_token:
            return JsonResponse({
                'status': 'error',
                'message': 'No access token provided'
            }, status=401)
        
        players = client.get_players()
        return JsonResponse({
            'status': 'success',
            'data': players
        })
    except Exception as e:
        print(f"Error in get_players view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_library(request):
    """Get library from Yoto API."""
    try:
        client = get_client_from_request(request)
        
        if not client.access_token:
            return JsonResponse({
                'status': 'error',
                'message': 'No access token provided'
            }, status=401)
        
        library = client.get_library()
        return JsonResponse({
            'status': 'success',
            'data': library
        })
    except Exception as e:
        print(f"Error in get_library view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_card_detail(request, card_id):
    """Get detailed card information including chapters."""
    try:
        print(f"=== get_card_detail called for card_id: {card_id} ===")
        client = get_client_from_request(request)
        
        print(f"Client access_token: {client.access_token[:20] if client.access_token else None}...")
        print(f"Client refresh_token: {client.refresh_token[:20] if client.refresh_token else None}...")
        print(f"Client client_id: {client.client_id[:20] if client.client_id else None}...")
        
        if not client.access_token:
            print("ERROR: No access token provided")
            return JsonResponse({
                'status': 'error',
                'message': 'No access token provided'
            }, status=401)
        
        print(f"Calling client.get_card({card_id})...")
        card = client.get_card(card_id, playable=True)
        print(f"Successfully retrieved card details")
        
        return JsonResponse({
            'status': 'success',
            'data': card
        })
    except Exception as e:
        print(f"!!! ERROR in get_card_detail view: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_player_detail(request, player_id):
    """Get specific player information."""
    try:
        client = YotoAPIClient()
        player_data = client.get_player(player_id)
        return JsonResponse({
            'status': 'success',
            'data': player_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
