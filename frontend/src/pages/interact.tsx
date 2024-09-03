import { Navbar } from "@/components/Navbar"
import { BottomNav } from "@/components/BottomNav"

export const InteractPage = () => {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <div className="container mx-auto">
                interact page
            </div>
            <BottomNav prevLink='/welcome' nextLink='/agents' currStep={1} disabled={true}></BottomNav>
        </div>
    )
}