import React from 'react';

interface ChatTableProps {
    data: any[];
}

export const ChatTable: React.FC<ChatTableProps> = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Flatten if data is an array of arrays (e.g. from backend AG2 list of lists)
    let processedData = data;
    if (Array.isArray(data[0])) {
        processedData = data.flat();
    }

    if (!processedData || processedData.length === 0 || typeof processedData[0] !== 'object') return null;

    const headers = Object.keys(processedData[0]);

    return (
        <div className="mt-4 overflow-x-auto border border-gray-200 dark:border-gray-700 rounded-lg">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700 text-sm">
                <thead className="bg-gray-50 dark:bg-gray-900/50">
                    <tr>
                        {headers.map((key) => (
                            <th
                                key={key}
                                className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap"
                            >
                                {key.replace(/_/g, ' ')}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {processedData.map((row, idx) => (
                        <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                            {Object.values(row).map((val: any, colIdx) => (
                                <td key={colIdx} className="px-4 py-2 whitespace-nowrap text-gray-700 dark:text-gray-300">
                                    {val !== null && val !== undefined ? String(val) : '-'}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
