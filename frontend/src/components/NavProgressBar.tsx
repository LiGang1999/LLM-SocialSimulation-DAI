import { useState } from "react";
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

import { GitHubLogoIcon } from "@radix-ui/react-icons";
import { buttonVariants } from "./ui/button";
import { Menu } from "lucide-react";
import { LogoIcon } from "./Icons";
import { Link } from "react-router-dom";

const github_link = 'https://github.com/ZJUCSS/social-experiment-platform'

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
        href: "#testimonials",
        label: "文档",
    },
    {
        href: "/templates",
        label: "仿真",
    },
    {
        href: "#pricing",
        label: "关于",
    },
    {
        href: "#faq",
        label: "FAQ",
    },
];

export const NavProgressBar = () => {
    const [isOpen, setIsOpen] = useState<boolean>(false);
    return (
        <header className="sticky border-b-[1px] top-0 z-40 w-full bg-white dark:border-b-slate-700 dark:bg-background">
            <NavigationMenu className="mx-auto">
                <NavigationMenuList className="container h-14 px-4 w-screen flex justify-between ">
                    <NavigationMenuItem className="font-bold flex">
                        <Link
                            rel="noreferrer noopener"
                            to="/"
                            className="ml-2 font-bold text-xl flex"
                        >
                            <LogoIcon />
                            LLM-SocialSimulation
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
                                    <Link
                                        rel="noreferrer noopener"
                                        to={github_link}
                                        className="w-[110px] border"
                                    >
                                        <GitHubLogoIcon className="mr-2 w-5 h-5" />
                                        Github
                                    </Link>
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
                                })}`}
                            >
                                {route.label}
                            </Link>
                        ))}
                    </nav>

                    <div className="hidden md:flex gap-2">
                        <Link
                            rel="noreferrer noopener"
                            to={github_link}
                            target="_blank"
                            className={`border ${buttonVariants({ variant: "ghost" })}`}
                        >
                            <GitHubLogoIcon className="mr-2 w-5 h-5" />
                            Github
                        </Link>

                    </div>
                </NavigationMenuList>
            </NavigationMenu>
        </header>
    );
};
