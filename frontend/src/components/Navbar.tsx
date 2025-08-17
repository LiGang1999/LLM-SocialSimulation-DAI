import { useState, useEffect } from "react";
import { X } from "lucide-react";
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuList,
} from "@/components/ui/navigation-menu";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
    DialogClose,
    DialogDescription,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Button, buttonVariants } from "./ui/button";
// import { GitHubLogoIcon } from "@radix-ui/react-icons";
import { Menu, MessageSquareText } from "lucide-react";
import { LogoIcon } from "./Icons";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { apis } from "@/lib/api"; // Import apis

// const github_link = 'https://github.com/ZJUCSS/social-experiment-platform'
const docs_link = '/doc/quickstart'

interface RouteProps {
    href: string;
    label: string;
}

const routeList: RouteProps[] = [
    {
        href: "/welcome",
        label: "首页",
    },
    {
        href: docs_link,
        label: "文档",
    },
    {
        href: "/templates",
        label: "仿真",
    },
    {
        href: "#about",
        label: "关于",
    },
    {
        href: "/doc/faq",
        label: "FAQ",
    },
];

interface NavbarProps {
    className?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ className }) => {
    const [isOpen, setIsOpen] = useState<boolean>(false);
    const [isFeedbackOpen, setIsFeedbackOpen] = useState<boolean>(false);
    const [feedbackText, setFeedbackText] = useState<string>("");
    const { user, isAuthenticated, logout } = useAuth();
    const [showBanner, setShowBanner] = useState(false);

    useEffect(() => {
        const bannerClosed = sessionStorage.getItem('bannerClosed');
        if (isAuthenticated && !bannerClosed) {
            setShowBanner(true);
        } else {
            setShowBanner(false);
        }
    }, [isAuthenticated]);

    const handleCloseBanner = () => {
        sessionStorage.setItem('bannerClosed', 'true');
        setShowBanner(false);
    };

    const handleFeedbackSubmit = async () => {
        if (!feedbackText.trim()) {
            alert("反馈内容不能为空");
            return;
        }
        if (!isAuthenticated || !user) {
            alert("请先登录再提交反馈");
            return;
        }

        const token = localStorage.getItem('token');
        if (!token) {
            alert("认证失败，请重新登录。");
            return;
        }

        try {
            // Use the new apis.submitFeedback function
            await apis.submitFeedback({
                username: user.username,
                feedback: feedbackText,
            });
            alert("反馈提交成功！感谢您的反馈。");
            setFeedbackText("");
            setIsFeedbackOpen(false);
        } catch (error) {
            // The apis.submitFeedback function already logs the error
            // and throws it, so we can catch it here for the alert.
            // Check if error has a response and a message property for more specific error messages
            let errorMessage = "提交反馈时发生错误。";
            if (error && typeof error === 'object' && 'response' in error && error.response &&
                typeof error.response === 'object' && 'data' in error.response && error.response.data &&
                typeof error.response.data === 'object' && 'message' in error.response.data) {
                errorMessage = `提交失败: ${error.response.data.message}`;
            } else if (error && typeof error === 'object' && 'message' in error) {
                errorMessage = `提交失败: ${error.message}`;
            }
            alert(errorMessage);
        }
    };

    return (
        <header className={`sticky top-0 z-40 w-full ${className}`}>
            <NavigationMenu className="mx-auto">
                <NavigationMenuList className="container h-14 px-4 w-screen flex justify-between ">
                    <NavigationMenuItem className="font-bold flex">
                        <Link
                            rel="noreferrer noopener"
                            to="/"
                            className="ml-2 font-bold text-xl flex"
                        >
                            <LogoIcon />
                            社会科学实验装置
                        </Link>
                    </NavigationMenuItem>

                    {/* mobile */}
                    <span className="flex md:hidden">

                        <Sheet
                            open={isOpen}
                            onOpenChange={setIsOpen}
                        >
                            <SheetTrigger className="px-2">
                                <Menu
                                    className="flex md:hidden h-5 w-5"
                                    onClick={() => setIsOpen(true)}
                                >
                                    <span className="sr-only">Menu Icon</span>
                                </Menu>
                            </SheetTrigger>

                            <SheetContent side={"left"}>
                                <SheetHeader>
                                    <SheetTitle className="font-bold text-xl">
                                        LLM-SocialSimulation
                                    </SheetTitle>
                                </SheetHeader>
                                <nav className="flex flex-col justify-center items-center gap-2 mt-4">
                                    {routeList.map(({ href, label }: RouteProps) => (
                                        <Link
                                            rel="noreferrer noopener"
                                            key={label}
                                            to={href}
                                            onClick={() => setIsOpen(false)}
                                            className={buttonVariants({ variant: "ghost" })}
                                        >
                                            {label}
                                        </Link>
                                    ))}
                                    {isAuthenticated ? (
                                        <>
                                            <span className={buttonVariants({ variant: "ghost" })}>
                                                {user?.username}
                                            </span>
                                            <Link
                                                rel="noreferrer noopener"
                                                to="/"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    logout();
                                                    setIsOpen(false);
                                                }}
                                                className="w-[110px] border-[1px] bg-gray-50 border-white border-opacity-40"
                                            >
                                                登出
                                            </Link>
                                        </>
                                    ) : (
                                        <>
                                            <Link
                                                rel="noreferrer noopener"
                                                to="/login"
                                                onClick={() => setIsOpen(false)}
                                                className="w-[110px] border-[1px] bg-gray-50 border-white border-opacity-40"
                                            >
                                                登录
                                            </Link>
                                            <Link
                                                rel="noreferrer noopener"
                                                to="/register"
                                                onClick={() => setIsOpen(false)}
                                                className="w-[110px] border-[1px] bg-gray-50 border-white border-opacity-40"
                                            >
                                                注册
                                            </Link>
                                        </>
                                    )}
                                    {/* <Link
                                        rel="noreferrer noopener"
                                        to={github_link}
                                        className="w-[110px] border-[1px] bg-gray-50 border-white border-opacity-40"
                                    >
                                        <GitHubLogoIcon className="mr-2 w-5 h-5" />
                                        Github
                                    </Link> */}
                                    <Button
                                        onClick={() => {
                                            setIsFeedbackOpen(true);
                                            setIsOpen(false);
                                        }}
                                        className="w-[110px] border-[1px] bg-blue-500 text-white border-white border-opacity-40"
                                    >
                                        <MessageSquareText className="mr-2 w-5 h-5" />
                                        反馈
                                    </Button>
                                    {isAuthenticated && user?.is_admin && (
                                        <Link
                                            rel="noreferrer noopener"
                                            to="/admin"
                                            onClick={() => setIsOpen(false)}
                                            className="w-[110px] border-[1px] bg-gray-50 border-white border-opacity-40"
                                        >
                                            管理后台
                                        </Link>
                                    )}
                                </nav>
                            </SheetContent>
                        </Sheet>
                    </span>

                    {/* desktop */}
                    <nav className="hidden md:flex gap-2">
                        {routeList.map((route: RouteProps, i) => (
                            <Link
                                rel="noreferrer noopener"
                                to={route.href}
                                key={i}
                                className={`text-[17px] ${buttonVariants({
                                    variant: "ghost",
                                })} bg-opacity-50`}
                            >
                                {route.label}
                            </Link>
                        ))}
                        {isAuthenticated && user?.is_admin && (
                            <Link
                                rel="noreferrer noopener"
                                to="/admin"
                                className={`text-[17px] ${buttonVariants({
                                    variant: "ghost",
                                })} bg-opacity-50`}
                            >
                                管理后台
                            </Link>
                        )}
                    </nav>

                    <div className="hidden md:flex gap-2">
                        {isAuthenticated ? (
                            <>
                                <Link
                                    rel="noreferrer noopener"
                                    to="/profile"
                                    className={`text-[17px] ${buttonVariants({
                                        variant: "ghost",
                                    })} bg-opacity-50`}
                                >
                                    {user?.username}
                                </Link>
                                <Link
                                    to="/"
                                    onClick={(e) => {
                                        e.preventDefault();
                                        logout();
                                    }}
                                    className={`border ${buttonVariants({ variant: "ghost" })} bg-white bg-opacity-20 border-opacity-40 border-white`}
                                >
                                    登出
                                </Link>
                            </>
                        ) : (
                            <>
                                <Link
                                    rel="noreferrer noopener"
                                    to="/login"
                                    className={`border ${buttonVariants({ variant: "ghost" })} bg-white bg-opacity-20 border-opacity-40 border-white`}
                                >
                                    登录
                                </Link>
                                <Link
                                    rel="noreferrer noopener"
                                    to="/register"
                                    className={`border ${buttonVariants({ variant: "ghost" })} bg-white bg-opacity-20 border-opacity-40 border-white`}
                                >
                                    注册
                                </Link>
                            </>
                        )}

                        {/* <Link
                            rel="noreferrer noopener"
                            to={github_link}
                            target="_blank"
                            className={`border ${buttonVariants({ variant: "ghost" })} bg-white bg-opacity-20 border-opacity-40 border-white`}
                        >
                            <GitHubLogoIcon className="mr-2 w-5 h-5" />
                            Github
                        </Link> */}
                        <Dialog open={isFeedbackOpen} onOpenChange={setIsFeedbackOpen}>
                            <DialogTrigger asChild>
                                <Button
                                    className={`border bg-blue-500 text-white border-opacity-40 border-white`}
                                >
                                    <MessageSquareText className="mr-2 w-5 h-5" />
                                    反馈
                                </Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-lg">
                                <DialogHeader>
                                    <DialogTitle>提交您的宝贵意见</DialogTitle>
                                    <DialogDescription>
                                        我们非常重视您的反馈，请告诉我们如何改进。
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="grid gap-6 py-4">
                                    <div className="grid w-full gap-2">
                                        <Label htmlFor="feedback-text" className="text-base font-medium">
                                            反馈内容：
                                        </Label>
                                        <Textarea
                                            id="feedback-text"
                                            value={feedbackText}
                                            onChange={(e) => setFeedbackText(e.target.value)}
                                            placeholder="请在此处详细描述您遇到的问题或建议..."
                                            className="min-h-[120px] text-sm p-3"
                                            rows={6}
                                        />
                                    </div>
                                </div>
                                <DialogFooter className="gap-2 sm:justify-end">
                                    <DialogClose asChild>
                                        <Button type="button" variant="outline">
                                            取消
                                        </Button>
                                    </DialogClose>
                                    <Button type="submit" onClick={handleFeedbackSubmit}>
                                        提交反馈
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </NavigationMenuList>
            </NavigationMenu>
            {showBanner && (
                <div className="bg-blue-100 border-b border-blue-200 text-blue-800 text-center p-2 text-sm relative">
                    为了使用本平台，请先前往<Link to="/profile" className="font-bold underline">个人主页</Link>配置您的 Providers
                    <button onClick={handleCloseBanner} className="absolute top-1/2 right-2 -translate-y-1/2">
                        <X className="h-4 w-4" />
                    </button>
                </div>
            )}
        </header>
    );
};
