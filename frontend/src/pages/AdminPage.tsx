import React, { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar'; // Assuming Navbar is in components
import { apis, FeedbackAdminItem } from '@/lib/api';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from '@/components/ui/scroll-area';

const AdminPage: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<FeedbackAdminItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeedbacks = async () => {
      try {
        setLoading(true);
        const data = await apis.getFeedbacks();
        setFeedbacks(data);
        setError(null);
      } catch (err) {
        setError('获取反馈列表失败。请稍后再试。');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchFeedbacks();
  }, []);

  return (
    <>
      <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
      <div className="container mx-auto p-4 mt-6">
        <h1 className="text-3xl font-bold mb-6 text-center">管理后台</h1>
        
        <Tabs defaultValue="feedbacks" className="w-full">
          <TabsList className="grid w-full grid-cols-1 mb-4"> {/* Adjust grid-cols as more tabs are added */}
            <TabsTrigger value="feedbacks">用户反馈</TabsTrigger>
            {/* Add more TabsTrigger here for other admin sections */}
          </TabsList>
          <TabsContent value="feedbacks">
            <div className="rounded-md border">
              <ScrollArea className="h-[600px]"> {/* Adjust height as needed */}
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[150px]">用户名</TableHead>
                      <TableHead className="w-[200px]">邮箱</TableHead>
                      <TableHead>反馈内容</TableHead>
                      <TableHead className="w-[200px] text-right">提交时间</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {loading ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center">
                          正在加载反馈数据...
                        </TableCell>
                      </TableRow>
                    ) : error ? (
                       <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center text-red-600">
                          {error}
                        </TableCell>
                      </TableRow>
                    ) : feedbacks.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center">
                          暂无反馈记录。
                        </TableCell>
                      </TableRow>
                    ) : (
                      feedbacks.map((fb) => (
                        <TableRow key={fb.id}>
                          <TableCell className="font-medium">{fb.user_username}</TableCell>
                          <TableCell>{fb.user_email}</TableCell>
                          <TableCell className="whitespace-pre-wrap break-words">{fb.feedback_text}</TableCell>
                          <TableCell className="text-right">
                            {new Date(fb.timestamp).toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </ScrollArea>
            </div>
          </TabsContent>
          {/* Add more TabsContent here */}
        </Tabs>
      </div>
    </>
  );
};

export default AdminPage;
