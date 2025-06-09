import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import backgroundImage from '@/assets/background2.jpg';
import { Navbar } from '@/components/Navbar';

export const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [institution, setInstitution] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('两次输入的密码不匹配');
      return;
    }

    setIsLoading(true);

    // Validate required fields
    if (!email || !fullName || !phone || !institution) {
      setError('请填写所有必填字段');
      return;
    }

    // Validate email format
    if (!/^\S+@\S+\.\S+$/.test(email)) {
      setError('请输入有效的电子邮件地址');
      return;
    }

    // Validate phone format (simple validation)
    if (!/^\d{10,15}$/.test(phone)) {
      setError('请输入有效的电话号码 (10-15位数字)');
      return;
    }

    try {
      const success = await register(
        username, 
        password, 
        email, 
        fullName, 
        phone, 
        institution
      );
      if (success) {
        navigate('/templates');
      } else {
        setError('注册失败，请重试');
      }
    } catch (err: any) {
      // Handle specific error cases
      if (err.response) {
        switch (err.response.status) {
          case 400:
            // Handle validation errors
            setError(err.response.data.detail || '用户名格式不正确或已被使用');
            break;
          default:
            setError('注册过程中出现错误');
        }
      } else {
        setError('注册过程中出现错误');
      }
      console.error(err);
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
          <CardTitle className="text-center text-2xl font-bold">注册</CardTitle>
          <CardDescription className="text-center">
            创建账号以使用社会科学实验装置
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                {error}
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              {/* Left Column */}
              <div className="space-y-3">
                <div className="space-y-1.5">
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
                <div className="space-y-1.5">
                  <Label htmlFor="email">电子邮件</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="fullName">全名</Label>
                  <Input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                    autoComplete="name"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="phone">电话号码</Label>
                  <Input
                    id="phone"
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    required
                    autoComplete="tel"
                  />
                </div>
              </div>
              
              {/* Right Column */}
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <Label htmlFor="institution">机构/单位</Label>
                  <Input
                    id="institution"
                    type="text"
                    value={institution}
                    onChange={(e) => setInstitution(e.target.value)}
                    required
                    autoComplete="organization"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="password">密码</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="confirmPassword">确认密码</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                  />
                </div>
              </div>
            </div>
            
            <Button type="submit" className="w-full mt-4" disabled={isLoading}>
              {isLoading ? '注册中...' : '注册'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="flex justify-center">
          <p className="text-sm text-gray-600">
            已有账号?{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              登录
            </Link>
          </p>
        </CardFooter>
      </Card>
      </div>
    </div>
  );
};

export default RegisterPage;
