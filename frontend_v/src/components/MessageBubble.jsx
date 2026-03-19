import React from 'react';

const UserAvatar = () => (
    <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4 text-gray-500 dark:text-gray-400">
            <path d="M10 8a3 3 0 100-6 3 3 0 000 6zM3.465 14.493a1.23 1.23 0 00.41 1.412A9.957 9.957 0 0010 18c2.31 0 4.438-.784 6.131-2.1.43-.333.604-.903.408-1.41a7.002 7.002 0 00-13.074.003z" />
        </svg>
    </div>
);

const AIAvatar = () => (
    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white text-sm shrink-0 shadow-sm">
        ✦
    </div>
);

export default function MessageBubble({ text, isUser, document_name }) {
    if (isUser) {
        return (
            <div className="flex items-end justify-end gap-3 py-1.5">
                <div className="max-w-[75%]">
                    {document_name && (
                        <div className="flex items-center gap-1.5 mb-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs px-3 py-1.5 rounded-full border border-blue-200 dark:border-blue-700 w-fit ml-auto">
                            <span>📄</span>
                            <span className="truncate max-w-[180px]">{document_name}</span>
                        </div>
                    )}
                    <div className="bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-br-sm text-sm leading-relaxed shadow-sm">
                        {text}
                    </div>
                </div>
                <UserAvatar />
            </div>
        );
    }

    return (
        <div className="flex items-start gap-3 py-1.5">
            <AIAvatar />
            <div className="max-w-[80%] bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
                <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">{text}</p>
            </div>
        </div>
    );
}
