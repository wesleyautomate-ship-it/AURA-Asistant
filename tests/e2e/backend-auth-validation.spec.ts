import { test, expect } from '@playwright/test';

test.describe('Backend Authentication Deep Dive', () => {
  // Test against backend directly
  test.use({ baseURL: 'http://localhost:8000' });

  test('should explore API structure and authentication patterns', async ({ request }) => {
    const findings: any = {
      timestamp: new Date().toISOString(),
      healthCheck: null,
      authEndpoints: [],
      protectedEndpoints: [],
      devEndpoints: [],
      publicEndpoints: [],
      disableAuthStatus: null
    };

    // Health check
    const healthResponse = await request.get('/health');
    findings.healthCheck = {
      status: healthResponse.status(),
      data: await healthResponse.json()
    };

    // Test common auth endpoints
    const authPaths = ['/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/refresh'];
    for (const path of authPaths) {
      try {
        const response = await request.get(path);
        findings.authEndpoints.push({
          path,
          status: response.status(),
          method: 'GET'
        });
      } catch (error) {
        findings.authEndpoints.push({
          path,
          error: 'Request failed',
          method: 'GET'
        });
      }
    }

    // Test protected endpoints
    const protectedPaths = [
      '/api/v1/properties/', 
      '/api/v1/users/me', 
      '/api/v1/clients/', 
      '/api/v1/tasks/',
      '/api/v1/ai/requests'
    ];
    
    for (const path of protectedPaths) {
      try {
        const response = await request.get(path);
        const data = response.status() < 500 ? await response.json() : null;
        findings.protectedEndpoints.push({
          path,
          status: response.status(),
          data: data,
          method: 'GET'
        });
      } catch (error) {
        findings.protectedEndpoints.push({
          path,
          error: 'Request failed',
          method: 'GET'
        });
      }
    }

    // Test potential dev endpoints
    const devPaths = [
      '/api/v1/properties/dev',
      '/api/v1/auth/dev', 
      '/api/v1/users/dev',
      '/api/v1/dev/status',
      '/dev/properties',
      '/dev/auth'
    ];
    
    for (const path of devPaths) {
      try {
        const response = await request.get(path);
        const data = response.status() < 500 ? await response.json() : null;
        findings.devEndpoints.push({
          path,
          status: response.status(),
          data: data,
          method: 'GET'
        });
      } catch (error) {
        findings.devEndpoints.push({
          path,
          error: 'Request failed',
          method: 'GET'  
        });
      }
    }

    // Test public endpoints
    const publicPaths = ['/docs', '/openapi.json', '/redoc', '/', '/health'];
    for (const path of publicPaths) {
      try {
        const response = await request.get(path);
        findings.publicEndpoints.push({
          path,
          status: response.status(),
          method: 'GET'
        });
      } catch (error) {
        findings.publicEndpoints.push({
          path,
          error: 'Request failed',
          method: 'GET'
        });
      }
    }

    // Log findings for analysis
    console.log('🔍 Backend API Analysis:', JSON.stringify(findings, null, 2));

    // Assertions for documentation
    expect(findings.healthCheck.status).toBe(200);
    expect(findings.healthCheck.data.status).toBe('healthy');

    // Check if DISABLE_AUTH is actually working
    const hasWorkingDevEndpoints = findings.devEndpoints.some(ep => ep.status === 200);
    const hasProtectedEndpointsWorking = findings.protectedEndpoints.some(ep => ep.status === 200);
    
    console.log(`📊 DISABLE_AUTH Analysis:
    - Has working dev endpoints: ${hasWorkingDevEndpoints}
    - Has protected endpoints working: ${hasProtectedEndpointsWorking}
    - Protected endpoints with 403: ${findings.protectedEndpoints.filter(ep => ep.status === 403).length}
    - Protected endpoints with other errors: ${findings.protectedEndpoints.filter(ep => ep.status !== 403 && ep.status !== 200).length}
    `);
  });

  test('should test authentication flow if login endpoint exists', async ({ request }) => {
    // Try to find and test authentication flow
    const loginAttempts = [
      { 
        path: '/api/v1/auth/login',
        body: { email: 'dev@example.com', password: 'devpassword' }
      },
      { 
        path: '/api/v1/auth/login',
        body: { username: 'dev@example.com', password: 'devpassword' }
      },
      { 
        path: '/api/v1/login',
        body: { email: 'dev@example.com', password: 'devpassword' }
      }
    ];

    const authResults: any[] = [];

    for (const attempt of loginAttempts) {
      try {
        const response = await request.post(attempt.path, {
          data: attempt.body,
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const responseData = response.status() < 500 ? await response.json() : null;
        
        authResults.push({
          path: attempt.path,
          status: response.status(),
          body: attempt.body,
          response: responseData
        });

        // If login successful, test authenticated request
        if (response.status() === 200 && responseData && responseData.access_token) {
          const authTestResponse = await request.get('/api/v1/properties/', {
            headers: {
              'Authorization': `Bearer ${responseData.access_token}`
            }
          });

          authResults.push({
            path: '/api/v1/properties/ (with token)',
            status: authTestResponse.status(),
            authenticated: true
          });
        }

      } catch (error) {
        authResults.push({
          path: attempt.path,
          error: 'Request failed'
        });
      }
    }

    console.log('🔐 Authentication Flow Results:', JSON.stringify(authResults, null, 2));

    // The test should pass regardless of auth results - we're gathering intel
    expect(authResults.length).toBeGreaterThan(0);
  });

  test('should test CORS and preflight requests', async ({ request }) => {
    // Test CORS behavior
    try {
      const corsResponse = await request.fetch('/api/v1/properties/', {
        method: 'OPTIONS',
        headers: {
          'Origin': 'http://localhost:5173',
          'Access-Control-Request-Method': 'GET',
          'Access-Control-Request-Headers': 'authorization,content-type'
        }
      });

      const corsHeaders = corsResponse.headers();
      
      console.log('🌐 CORS Analysis:', {
        status: corsResponse.status(),
        headers: corsHeaders,
        allowOrigin: corsHeaders['access-control-allow-origin'],
        allowMethods: corsHeaders['access-control-allow-methods'],
        allowHeaders: corsHeaders['access-control-allow-headers']
      });

    } catch (error) {
      console.log('🌐 CORS test failed:', error);
    }

    // Always pass - this is investigative
    expect(true).toBe(true);
  });
});