"use client";

import { useRouter } from "next/navigation";
import { LogOut, Building2 } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  company: string;
}

export function Header({ company }: HeaderProps) {
  const router = useRouter();
  const supabase = createClient();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  };

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 sm:px-6 lg:px-8">
      <div className="flex items-center">
        <Building2 className="h-5 w-5 text-gray-400 mr-2" />
        <span className="text-sm font-medium text-gray-700">{company}</span>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleLogout}
        className="text-gray-500 hover:text-gray-700"
      >
        <LogOut className="h-4 w-4 mr-2" />
        Sair
      </Button>
    </header>
  );
}
