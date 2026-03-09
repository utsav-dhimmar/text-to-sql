import { Building2 } from "lucide-react";
import { Button } from "../ui";

interface DataManagementSectionProps {
  sectorName: string;
  companyName: string;
  industryId: number | "";
  formMessage: string | null;
  onSectorNameChange: (value: string) => void;
  onCompanyNameChange: (value: string) => void;
  onIndustryIdChange: (value: number | "") => void;
  onCreateSector: () => void;
  onCreateCompany: () => void;
}

export function DataManagementSection({
  sectorName,
  companyName,
  industryId,
  formMessage,
  onSectorNameChange,
  onCompanyNameChange,
  onIndustryIdChange,
  onCreateSector,
  onCreateCompany,
}: DataManagementSectionProps) {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden flex flex-col">
      <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-center bg-gray-50/50 dark:bg-zinc-900/50">
        <h2 className="text-xl font-bold dark:text-white flex items-center gap-2">
          <Building2 className="text-amber-500" size={20} />
          Data Management
        </h2>
      </div>
      <div className="p-6 space-y-6">
        <div>
          <p className="text-sm font-semibold text-gray-700 dark:text-zinc-300">
            Create Sector
          </p>
          <div className="mt-3 flex flex-col sm:flex-row gap-3">
            <input
              value={sectorName}
              onChange={(e) => onSectorNameChange(e.target.value)}
              placeholder="Sector name"
              className="flex-1 rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
            />
            <Button onClick={onCreateSector} disabled={!sectorName}>
              Add Sector
            </Button>
          </div>
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-700 dark:text-zinc-300">
            Create Company
          </p>
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-[1fr,150px,auto] gap-3">
            <input
              value={companyName}
              onChange={(e) => onCompanyNameChange(e.target.value)}
              placeholder="Company name"
              className="rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
            />
            <input
              type="number"
              min={1}
              value={industryId}
              onChange={(e) =>
                onIndustryIdChange(e.target.value ? Number(e.target.value) : "")
              }
              placeholder="Industry ID"
              className="rounded-lg border border-gray-200 dark:border-zinc-700 bg-white dark:bg-zinc-950 px-3 py-2 text-sm text-gray-700 dark:text-zinc-200"
            />
            <Button
              onClick={onCreateCompany}
              disabled={!companyName || !industryId}
            >
              Add Company
            </Button>
          </div>
        </div>
        {formMessage && <p className="text-sm text-indigo-500">{formMessage}</p>}
      </div>
    </div>
  );
}
