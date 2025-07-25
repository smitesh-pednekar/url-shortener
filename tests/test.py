import pytest
import json
from datetime import datetime
from app.main import app
from app.models import url_store, URLMapping

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_store():
    """Clear the URL store before each test."""
    url_store._mappings.clear()

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_api_health(client):
    """Test the API health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'URL Shortener API is running' in data['message']

def test_shorten_url_success(client):
    """Test successful URL shortening."""
    response = client.post('/api/shorten',
                          json={'url': 'https://www.example.com/very/long/url'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data
    assert 'short_url' in data
    assert len(data['short_code']) == 6
    assert data['short_url'].endswith(data['short_code'])

def test_shorten_url_with_http(client):
    """Test URL shortening with http protocol."""
    response = client.post('/api/shorten',
                          json={'url': 'http://example.com'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data
    assert len(data['short_code']) == 6

def test_shorten_url_without_protocol(client):
    """Test URL shortening without protocol (should be normalized)."""
    response = client.post('/api/shorten',
                          json={'url': 'example.com'},
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'short_code' in data

def test_shorten_invalid_url(client):
    """Test shortening with invalid URL."""
    response = client.post('/api/shorten',
                          json={'url': 'invalid-url'},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid URL format' in data['error']

def test_shorten_empty_url(client):
    """Test shortening with empty URL."""
    response = client.post('/api/shorten',
                          json={'url': ''},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_shorten_missing_url(client):
    """Test shortening without URL field."""
    response = client.post('/api/shorten',
                          json={},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'URL is required' in data['error']

def test_shorten_non_json(client):
    """Test shortening with non-JSON request."""
    response = client.post('/api/shorten',
                          data='not json',
                          content_type='text/plain')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Request must be JSON' in data['error']

def test_redirect_success(client):
    """Test successful redirect."""
    # First, create a short URL
    response = client.post('/api/shorten',
                          json={'url': 'https://www.example.com'},
                          content_type='application/json')
    
    assert response.status_code == 201
    short_code = response.get_json()['short_code']
    
    # Test redirect
    response = client.get(f'/{short_code}')
    assert response.status_code == 302
    assert response.location == 'https://www.example.com'

def test_redirect_not_found(client):
    """Test redirect with non-existent short code."""
    response = client.get('/abcdef')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Short code not found' in data['error']

def test_redirect_invalid_format(client):
    """Test redirect with invalid short code format."""
    response = client.get('/abc')  # Too short
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_stats_success(client):
    """Test successful stats retrieval."""
    # First, create a short URL
    response = client.post('/api/shorten',
                          json={'url': 'https://www.example.com'},
                          content_type='application/json')
    
    assert response.status_code == 201
    short_code = response.get_json()['short_code']
    
    # Get stats (should have 0 clicks initially)
    response = client.get(f'/api/stats/{short_code}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['url'] == 'https://www.example.com'
    assert data['clicks'] == 0
    assert 'created_at' in data
    assert data['short_code'] == short_code

def test_stats_with_clicks(client):
    """Test stats after redirects."""
    # Create a short URL
    response = client.post('/api/shorten',
                          json={'url': 'https://www.example.com'},
                          content_type='application/json')
    
    short_code = response.get_json()['short_code']
    
    # Access the short URL a few times
    client.get(f'/{short_code}')
    client.get(f'/{short_code}')
    client.get(f'/{short_code}')
    
    # Check stats
    response = client.get(f'/api/stats/{short_code}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['clicks'] == 3

def test_stats_not_found(client):
    """Test stats for non-existent short code."""
    response = client.get('/api/stats/abcdef')
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'Short code not found' in data['error']

def test_concurrent_access(client):
    """Test that concurrent access works properly."""
    import threading
    
    # Create a short URL
    response = client.post('/api/shorten',
                          json={'url': 'https://www.example.com'},
                          content_type='application/json')
    
    short_code = response.get_json()['short_code']
    
    # Function to access the URL multiple times
    def access_url():
        for _ in range(10):
            client.get(f'/{short_code}')
    
    # Create multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=access_url)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check final click count
    response = client.get(f'/api/stats/{short_code}')
    data = response.get_json()
    assert data['clicks'] == 50  # 5 threads * 10 accesses each

def test_url_mapping_model():
    """Test the URLMapping model."""
    mapping = URLMapping('https://example.com', 'abc123')
    
    assert mapping.original_url == 'https://example.com'
    assert mapping.short_code == 'abc123'
    assert mapping.clicks == 0
    assert isinstance(mapping.created_at, datetime)
    
    # Test increment clicks
    mapping.increment_clicks()
    assert mapping.clicks == 1
    
    # Test to_dict
    data = mapping.to_dict()
    assert data['url'] == 'https://example.com'
    assert data['short_code'] == 'abc123'
    assert data['clicks'] == 1
    assert 'created_at' in data

def test_unique_short_codes(client):
    """Test that generated short codes are unique."""
    short_codes = set()
    
    # Generate multiple short URLs
    for i in range(20):
        response = client.post('/api/shorten',
                              json={'url': f'https://example{i}.com'},
                              content_type='application/json')
        
        assert response.status_code == 201
        short_code = response.get_json()['short_code']
        assert short_code not in short_codes
        short_codes.add(short_code)
    
    assert len(short_codes) == 20
