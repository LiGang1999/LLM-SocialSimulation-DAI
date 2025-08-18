import React, { useEffect, useState } from 'react';
import { Navbar } from '@/components/Navbar'; // Assuming Navbar is in components
import { apis, FeedbackAdminItem, AdminTemplate, User } from '@/lib/api';
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
import { Button } from '@/components/ui/button';
import { ArrowUpDown, Calendar as CalendarIcon } from 'lucide-react';
import { Toaster, toast } from 'sonner';
import { DateRange } from 'react-day-picker';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

type TemplateSortKey = keyof AdminTemplate | 'name' | 'username' | 'description' | 'creation_time' | 'agent_count';
type UserSortKey = keyof User | 'username' | 'full_name' | 'email' | 'institution';

const AdminPage: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<FeedbackAdminItem[]>([]);
  const [templates, setTemplates] = useState<AdminTemplate[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [templatesLoading, setTemplatesLoading] = useState<boolean>(true);
  const [templatesError, setTemplatesError] = useState<string | null>(null);
  const [usersLoading, setUsersLoading] = useState<boolean>(true);
  const [usersError, setUsersError] = useState<string | null>(null);
  const [templateSortKey, setTemplateSortKey] = useState<TemplateSortKey>('creation_time');
  const [templateSortOrder, setTemplateSortOrder] = useState<'asc' | 'desc'>('desc');
  const [userSortKey, setUserSortKey] = useState<UserSortKey>('username');
  const [userSortOrder, setUserSortOrder] = useState<'asc' | 'desc'>('asc');
  const [date, setDate] = useState<DateRange | undefined>(undefined);

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

    const fetchTemplates = async () => {
      try {
        setTemplatesLoading(true);
        const data = await apis.getAllUserTemplates();
        setTemplates(data);
        setTemplatesError(null);
      } catch (err) {
        setTemplatesError('获取用户模板列表失败。请稍后再试。');
        console.error(err);
      } finally {
        setTemplatesLoading(false);
      }
    };

    const fetchUsers = async () => {
      try {
        setUsersLoading(true);
        const data = await apis.getAllUsers();
        setUsers(data);
        setUsersError(null);
      } catch (err) {
        setUsersError('获取用户列表失败。请稍后再试。');
        console.error(err);
      } finally {
        setUsersLoading(false);
      }
    };

    fetchFeedbacks();
    fetchTemplates();
    fetchUsers();
  }, []);

  const handleRefreshTemplates = async () => {
    try {
      setTemplatesLoading(true);
      const data = await apis.getAllUserTemplates();
      setTemplates(data);
      setTemplatesError(null);
    } catch (err) {
      setTemplatesError('获取用户模板列表失败。请稍后再试。');
      console.error(err);
    } finally {
      setTemplatesLoading(false);
    }
  };

  const handleCopyToCSV = () => {
    const headers = ["Template Name", "Username", "Description", "Agents", "Creation Time"];
    const rows = filteredTemplates.map(template => [
      `"${template.meta.name}"`,
      `"${template.username}"`,
      `"${template.meta.description.replace(/"/g, '""')}"`,
      `"${template.meta.persona_names.join(', ')}"`,
      `"${new Date(template.creation_time * 1000).toLocaleString()}"`
    ]);

    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(csvContent).then(() => {
        toast.success('已复制到剪贴板');
      }, (err) => {
        toast.error('复制失败');
        console.error('Could not copy text: ', err);
      });
    } else {
      // Fallback for insecure contexts
      const textArea = document.createElement("textarea");
      textArea.value = csvContent;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        toast.success('已复制到剪贴板');
      } catch (err) {
        toast.error('复制失败');
        console.error('Could not copy text: ', err);
      }
      document.body.removeChild(textArea);
    }
  };

  const handleTemplateSort = (key: TemplateSortKey) => {
    if (templateSortKey === key) {
      setTemplateSortOrder(templateSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setTemplateSortKey(key);
      setTemplateSortOrder('asc');
    }
  };

  const handleUserSort = (key: UserSortKey) => {
    if (userSortKey === key) {
      setUserSortOrder(userSortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setUserSortKey(key);
      setUserSortOrder('asc');
    }
  };

  const sortedTemplates = [...templates].sort((a, b) => {
    let aValue: any;
    let bValue: any;

    if (templateSortKey === 'name' || templateSortKey === 'description') {
      aValue = a.meta[templateSortKey];
      bValue = b.meta[templateSortKey];
    } else if (templateSortKey === 'agent_count') {
        aValue = a.meta.persona_names.length;
        bValue = b.meta.persona_names.length;
    } 
    else {
      aValue = a[templateSortKey as keyof AdminTemplate];
      bValue = b[templateSortKey as keyof AdminTemplate];
    }

    if (aValue < bValue) {
      return templateSortOrder === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return templateSortOrder === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const filteredTemplates = sortedTemplates.filter(template => {
    if (!date?.from) return true;
    const from = new Date(date.from);
    from.setHours(0, 0, 0, 0);

    const to = date.to ? new Date(date.to) : new Date();
    to.setHours(23, 59, 59, 999);
    
    const templateDate = new Date(template.creation_time * 1000);
    return templateDate >= from && templateDate <= to;
  });

  const sortedUsers = [...users].sort((a, b) => {
    const aValue = a[userSortKey as keyof User] || '';
    const bValue = b[userSortKey as keyof User] || '';

    if (aValue < bValue) {
      return userSortOrder === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return userSortOrder === 'asc' ? 1 : -1;
    }
    return 0;
  });

  const formatAgentNames = (names: string[]) => {
    const max_shown = 3;
    if (names.length <= max_shown) {
      return names.join(', ');
    }
    const shown_names = names.slice(0, max_shown).join(', ');
    return `${shown_names}, and ${names.length - max_shown} more...`;
  };

  return (
    <>
      <Toaster />
      <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
      <div className="container mx-auto p-4 mt-6">
        <h1 className="text-3xl font-bold mb-6 text-center">管理后台</h1>
        
        <Tabs defaultValue="feedbacks" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="feedbacks">用户反馈</TabsTrigger>
            <TabsTrigger value="templates">用户模板</TabsTrigger>
            <TabsTrigger value="users">用户管理</TabsTrigger>
          </TabsList>
          <TabsContent value="feedbacks">
            <div className="rounded-md border">
              <ScrollArea className="h-[600px]">
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
          <TabsContent value="templates">
            <div className="flex justify-between mb-4">
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    id="date"
                    variant={"outline"}
                    className={cn(
                      "w-[300px] justify-start text-left font-normal",
                      !date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date?.from ? (
                      date.to ? (
                        <>
                          {format(date.from, "LLL dd, y")} -{" "}
                          {format(date.to, "LLL dd, y")}
                        </>
                      ) : (
                        format(date.from, "LLL dd, y")
                      )
                    ) : (
                      <span>选择日期范围</span>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    initialFocus
                    mode="range"
                    defaultMonth={date?.from}
                    selected={date}
                    onSelect={setDate}
                    numberOfMonths={2}
                  />
                </PopoverContent>
              </Popover>
              <div>
                <Button onClick={handleCopyToCSV} className="mr-2">复制为CSV</Button>
                <Button onClick={handleRefreshTemplates} disabled={templatesLoading}>
                  {templatesLoading ? '刷新中...' : '刷新'}
                </Button>
              </div>
            </div>
            <div className="rounded-md border">
              <ScrollArea className="h-[600px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[200px]">
                        <Button variant="ghost" onClick={() => handleTemplateSort('name')}>
                          模板名称
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead className="w-[150px]">
                        <Button variant="ghost" onClick={() => handleTemplateSort('username')}>
                          用户名
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button variant="ghost" onClick={() => handleTemplateSort('description')}>
                          描述
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead className="w-[200px]">
                        <Button variant="ghost" onClick={() => handleTemplateSort('agent_count')}>
                          智能体
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead className="w-[200px] text-right">
                        <Button variant="ghost" onClick={() => handleTemplateSort('creation_time')}>
                          创建时间
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {templatesLoading ? (
                      <TableRow>
                        <TableCell colSpan={5} className="h-24 text-center">
                          正在加载用户模板...
                        </TableCell>
                      </TableRow>
                    ) : templatesError ? (
                      <TableRow>
                        <TableCell colSpan={5} className="h-24 text-center text-red-600">
                          {templatesError}
                        </TableCell>
                      </TableRow>
                    ) : filteredTemplates.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className="h-24 text-center">
                          暂无用户模板。
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredTemplates.map((template, index) => (
                        <TableRow key={`${template.meta.template_sim_code}-${template.username}-${index}`}>
                          <TableCell className="font-medium">{template.meta.name}</TableCell>
                          <TableCell>{template.username}</TableCell>
                          <TableCell className="whitespace-pre-wrap break-words">{template.meta.description}</TableCell>
                          <TableCell>{formatAgentNames(template.meta.persona_names)}</TableCell>
                          <TableCell className="text-right">
                            {new Date(template.creation_time * 1000).toLocaleString()}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </ScrollArea>
            </div>
          </TabsContent>
          <TabsContent value="users">
            <div className="rounded-md border">
              <ScrollArea className="h-[600px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>
                        <Button variant="ghost" onClick={() => handleUserSort('username')}>
                          用户名
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button variant="ghost" onClick={() => handleUserSort('full_name')}>
                          姓名
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button variant="ghost" onClick={() => handleUserSort('email')}>
                          邮箱
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button variant="ghost" onClick={() => handleUserSort('institution')}>
                          机构
                          <ArrowUpDown className="ml-2 h-4 w-4" />
                        </Button>
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {usersLoading ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center">
                          正在加载用户数据...
                        </TableCell>
                      </TableRow>
                    ) : usersError ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center text-red-600">
                          {usersError}
                        </TableCell>
                      </TableRow>
                    ) : sortedUsers.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center">
                          暂无用户记录。
                        </TableCell>
                      </TableRow>
                    ) : (
                      sortedUsers.map((user) => (
                        <TableRow key={user.username}>
                          <TableCell>{user.username}</TableCell>
                          <TableCell>{user.full_name}</TableCell>
                          <TableCell>{user.email}</TableCell>
                          <TableCell>{user.institution}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </ScrollArea>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </>
  );
};

export default AdminPage;
