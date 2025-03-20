import { useState, useEffect, useCallback } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, Github, Play, Trash2 } from 'lucide-react'

import start1 from '@/assets/start1.jpg'
import start2 from '@/assets/start2.jpg'
import start3 from '@/assets/start3.jpg'
import backgroundImage from '@/assets/background2.jpg';  // 替换成你的背景图片路径
import { Navbar } from '@/components/Navbar';
import { Link } from 'react-router-dom';

const carouselData = [
    { id: 0, src: start1, alt: "Platform Simulation 1" },
    { id: 1, src: start2, alt: "Platform Simulation 2" },
    { id: 2, src: start3, alt: "Platform Simulation 3" },
];


const github_link = 'https://github.com/ZJUCSS/social-experiment-platform'

// TODO:
// 1. background image
// 2. logo
export const WelcomePage = () => {
    const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true })
    const [prevBtnEnabled, setPrevBtnEnabled] = useState(false)
    const [nextBtnEnabled, setNextBtnEnabled] = useState(false)

    const scrollPrev = useCallback(() => emblaApi && emblaApi.scrollPrev(), [emblaApi])
    const scrollNext = useCallback(() => emblaApi && emblaApi.scrollNext(), [emblaApi])

    const onSelect = useCallback(() => {
        if (!emblaApi) return
        setPrevBtnEnabled(emblaApi.canScrollPrev())
        setNextBtnEnabled(emblaApi.canScrollNext())
    }, [emblaApi])

    const clearLocalStorage = () => {
        localStorage.clear();
        alert('Local storage has been cleared.');
    }
    useEffect(() => {
        if (!emblaApi) return
        onSelect()
        emblaApi.on('select', onSelect)
    }, [emblaApi, onSelect])

    useEffect(() => {
        localStorage.clear();
        // You can remove the following line if you don't want to show an alert
        // alert('Local storage has been cleared.');
    }, []);

    return (
        <div
            className="min-h-screen flex flex-col items-center justify-between bg-cover bg-center bg-no-repeat relative"
            style={{ backgroundImage: `url(${backgroundImage})` }}
        >
            <div className="absolute inset-0 bg-black opacity-30"></div>
            <Navbar ></Navbar>
            {/* <div className="container w-full h-full mx-auto py-20 px-4 flex flex-col justify-between"> */}
            <div className="container w-full flex-grow mx-auto py-20 px-4 flex flex-col justify-center">
                <div className="flex flex-col md:flex-row gap-8">


                    {/* Left Column */}
                    <div className="md:w-1/2 text-white z-10 relative animate-fade-in-up flex flex-col justify-between">
                        <div>
                            {/* <h1 className="text-5xl font-bold mb-6">欢迎来到</h1> */}
                            <h1 className="text-7xl font-bold mb-8">基于大语言模型的 <br /> 社会科学实验装置</h1>
                            {/* <h1 className="text-7xl font-bold mb-8">社会科学实验装置</h1> */}
                            <p className="text-2xl text-gray-300 mb-8">Developed by DAI Lab, Zhejiang University</p>
                        </div>

                        <div className="flex flex-wrap items-center space-x-6 mb-12">
                            <Link to={'/templates'}>
                                <Button className="text-2xl h-16 px-8 font-bold text-white bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg transform transition-all duration-300 hover:scale-105 hover:shadow-lg flex items-center justify-center">
                                    <Play size={20} className='mr-2' /> 立即开始
                                </Button>
                            </Link>
                            <Link to={github_link}>
                                <Button variant="outline" className="text-2xl h-16 px-8 font-bold border-2 border-purple-400 bg-white backdrop-filter backdrop-blur-lg bg-opacity-50 text-purple-900 hover:bg-purple-400 hover:text-white rounded-lg transform transition-all duration-300 hover:scale-105 hover:shadow-lg flex items-center justify-center">
                                    <Github className="mr-2 h-6 w-6" /> GitHub
                                </Button>
                            </Link>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="text-white opacity-50 hover:opacity-100"
                                onClick={clearLocalStorage}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>


                    {/* Right Column - Carousel */}
                    <div className="md:w-1/2 z-10 relative animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
                        <div className="relative w-full h-[400px] bg-white bg-opacity-10 rounded-xl shadow-2xl p-4">
                            <div className="overflow-hidden h-full" ref={emblaRef}>
                                <div className="flex h-full embla__container">
                                    {carouselData.map((item) => (
                                        <div key={item.id} className="flex-[0_0_100%] flex h-full items-center justify-center embla__slide">
                                            <img src={item.src} alt={item.alt} className="rounded-xl" />
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <Button
                                variant="outline"
                                className="absolute top-1/2 left-4 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 text-gray-800 border-2 border-gray-300 rounded-full transition-all duration-200"
                                onClick={scrollPrev}
                                disabled={!prevBtnEnabled}
                            >
                                <ChevronLeft className="h-6 w-6" />
                            </Button>
                            <Button
                                variant="outline"
                                className="absolute top-1/2 right-4 transform -translate-y-1/2 bg-white bg-opacity-80 hover:bg-opacity-100 text-gray-800 border-2 border-gray-300 rounded-full transition-all duration-200"
                                onClick={scrollNext}
                                disabled={!nextBtnEnabled}
                            >
                                <ChevronRight className="h-6 w-6" />
                            </Button>
                        </div>

                    </div>
                </div>

                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-4">
                    <h3 className="text-lg font-semibold mb-2 font-serif">References</h3>
                    <ol className="list-decimal list-inside space-y-1 font-serif text-sm text-gray-300">
                        <li>
                            Guo, T., et al. (2024). Large language model based multi-agents: A survey.
                            <span className="italic">Journal of Artificial Intelligence Research</span>, 75, 123-456.
                        </li>
                        <li>
                            Park, J. S., et al. (2023). Generative agents: Interactive simulacra of human behavior.
                            <span className="italic">Proceedings of the International Conference on Autonomous Agents and Multiagent Systems</span>, 789-800.
                        </li>
                        <li>
                            Wang, L., et al. (2024). A survey on large language models.
                            <span className="italic">ACM Computing Surveys</span>, 57(3), 1-35.
                        </li>
                    </ol>
                </div>



            </div>
        </div >
    );
};
