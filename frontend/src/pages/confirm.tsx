import { Navbar } from "@/components/Navbar"

import { BottomNav } from "@/components/BottomNav"


export const ConfirmPage = () => {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">开始仿真</h2>

                <BottomNav prevLink='/llmconfig' nextLink='#' currStep={4} disabled={false} className='mt-16'></BottomNav>
            </div>
        </div>
    )
}