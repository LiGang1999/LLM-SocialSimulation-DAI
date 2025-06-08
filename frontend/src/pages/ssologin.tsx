import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apis } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

const SSOLogin: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { ssoLogin } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const performSSOLogin = async () => {
      try {
        // Get SSO parameters from URL
        const appId = searchParams.get('appId');
        const username = searchParams.get('username');
        const time = searchParams.get('time');
        const sign = searchParams.get('sign');

        // Validate required parameters
        if (!appId || !username || !time || !sign) {
          setError('缺少必要的SSO参数');
          setLoading(false);
          return;
        }

        const data = await apis.ssoLogin({ appId, username, time, sign });

        await ssoLogin(data.access_token);

        // Navigate to the dashboard
        navigate('/welcome', { replace: true });

      } catch (err) {
        console.error('SSO login error:', err);
        setError(err instanceof Error ? err.message : 'SSO登录失败，请重试');
        setLoading(false);
      }
    };

    performSSOLogin();
  }, [searchParams, navigate, ssoLogin]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>单点登录</CardTitle>
          <CardDescription>正在通过单点登录系统进行身份验证...</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="text-sm text-gray-600">正在验证您的身份，请稍候...</p>
            </div>
          ) : error ? (
            <div className="flex items-start space-x-2 text-red-600">
              <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          ) : (
            <div className="flex items-start space-x-2 text-green-600">
              <CheckCircle2 className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <p className="text-sm">登录成功！正在跳转...</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SSOLogin;
