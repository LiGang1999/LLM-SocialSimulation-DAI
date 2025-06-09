import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import backgroundImage from '@/assets/background2.jpg';
import { Navbar } from '@/components/Navbar';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.message) {
      setError(location.state.message);
    }
  }, [location.state]);

  // Get the redirect path from location state or default to /templates
  const from = location.state?.from?.pathname || '/templates';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const success = await login(username, password);
      if (success) {
        navigate(from, { replace: true });
      } else {
        setError('用户名或密码错误');
      }
    } catch (err: any) {
      if (err.response && err.response.status === 401) {
        setError('用户名或密码错误');
      } else {
        setError('登录过程中出现错误，请重试');
        console.error(err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-cover bg-center bg-no-repeat relative" style={{ backgroundImage: `url(${backgroundImage})` }}>
      <div className="absolute inset-0 bg-black opacity-30"></div>
      <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
      <div className="flex-grow flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8 w-full">
        <Card className="w-full max-w-md z-10 relative animate-fade-in-up">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold">登录</CardTitle>
            <CardDescription className="text-center">
              登录以继续使用社会科学实验装置
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="username">用户名</Label>
                <Input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">密码</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? '登录中...' : '登录'}
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex justify-center">
            <p className="text-sm text-gray-600">
              还没有账号?{' '}
              <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
                注册
              </Link>
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default LoginPage;
