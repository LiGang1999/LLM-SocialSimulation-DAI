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

        const faceColors = ['#F7C3A7', '#F4B2B2', '#F0B287', '#FFCEA6', '#E6A17A', '#F3D1C0']; // Expanded skin tones
        const hairColors = ['#3F2E1A', '#7A3F1A', '#9E593C', '#B5815E', '#C09774', '#6A503D', '#5E3923', '#8B6B4F']; // More brown and auburn options
        const hatColors = ['#333333', '#D4C568', '#D45F54', '#6C89B5', '#F2F2F2', '#B4A07D', '#8F7161', '#476078']; // Muted but vivid hat colors
        const shirtColors = ['#9B5C3A', '#F7A3AA', '#BCE6EB', '#6881D1', '#E38D5C', '#7F9C6E', '#F4BA7B', '#8C70B1']; // Wider range of earthy, vivid colors for shirts
        const bgColors = ['#D7E5F1', '#F3D9BF', '#CBCDE6', '#D8ECD8', '#F4D3D8', '#ECE7C8', '#F1E1DF', '#CFE1F1']; // Expanded background colors for variety



        return genConfig({
            sex: getOption(['man', 'woman']),
            faceColor: getOption(faceColors),
            earSize: getOption(['small', 'big']),
            hairColor: getOption(hairColors),
            hairStyle: getOption(['normal', 'thick', 'mohawk', 'womanLong', 'womanShort']),
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