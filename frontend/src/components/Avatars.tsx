import React, { useMemo } from 'react';
import Avatar, { genConfig, NiceAvatarProps, AvatarFullConfig } from 'react-nice-avatar';

interface RandomAvatarProps extends Omit<NiceAvatarProps, keyof AvatarFullConfig> {
    name: string;
}

export const RandomAvatar: React.FC<RandomAvatarProps> = ({ name, ...props }) => {
    const config = useMemo((): AvatarFullConfig => {
        const hashName = (str: string): number => {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                const char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32-bit integer
            }
            return Math.abs(hash);
        };

        const seed = hashName(name);

        const getOption = <T,>(options: T[]): T => {
            return options[seed % options.length];
        };


        const faceColors = ['#F7C3A7', '#F4B2B2', '#F0B287', '#FFCEA6', '#E6A17A', '#F3D1C0', '#FFD1DC', '#FFDAB9'];
        const hairColors = ['#090806', '#2C222B', '#71635A', '#B7A69E', '#D6C4C2', '#DEBA9D', '#85776E', '#A7856A', '#E5C8A8', '#DEBC99'];
        const hatColors = ['#333333', '#D4C568', '#D45F54', '#6C89B5', '#F2F2F2', '#B4A07D', '#8F7161', '#476078', '#7CB9E8', '#C04000'];
        const shirtColors = ['#9B5C3A', '#F7A3AA', '#BCE6EB', '#6881D1', '#E38D5C', '#7F9C6E', '#F4BA7B', '#8C70B1', '#50C878', '#FF6B6B'];
        const bgColors = [
            '#FFD1DC', // Light pink
            '#AFEEEE', // Pale turquoise
            '#98FB98', // Pale green
            '#FFA07A', // Light salmon
            '#87CEFA', // Light sky blue
            '#DDA0DD', // Plum
            '#FAFAD2', // Light goldenrod yellow
            '#B0E0E6', // Powder blue
            '#FFDAB9', // Peach puff
            '#E6E6FA', // Lavender
            '#F0FFF0', // Honeydew
            '#FFF0F5', // Lavender blush
            '#F0FFFF', // Azure
            '#F5DEB3', // Wheat
        ];



        return genConfig({
            sex: getOption(['man', 'woman']),
            faceColor: getOption(faceColors),
            earSize: getOption(['small', 'big']),
            hairColor: getOption(hairColors),
            hairStyle: getOption(['normal', 'thick', 'womanLong', 'womanShort']),
            hatColor: getOption(hatColors),
            hatStyle: getOption(['beanie', 'turban', 'none']),
            eyeStyle: getOption(['circle', 'oval', 'smile']),
            glassesStyle: getOption(['round', 'square', 'none']),
            noseStyle: getOption(['short', 'long', 'round']),
            mouthStyle: getOption(['laugh', 'smile', 'peace']),
            shirtStyle: getOption(['hoody', 'short', 'polo']),
            shirtColor: getOption(shirtColors),
            bgColor: getOption(bgColors),
        });
    }, [name]);

    return <Avatar {...props} {...config} />;
};