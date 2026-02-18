"use client";

import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import type { User } from "@/types";

interface ProfileHeaderProps {
  user: User;
}

export function ProfileHeader({ user }: ProfileHeaderProps) {
  const fullName = `${user.first_name} ${user.last_name}`;

  return (
    <div className="flex items-center gap-5">
      <Avatar src={user.avatar_url} name={fullName} size="lg" />
      <div>
        <h1 className="text-xl font-bold text-text-primary">{fullName}</h1>
        <p className="text-sm text-text-secondary">{user.email}</p>
        {user.major && (
          <Badge variant="green" className="mt-2">
            {user.major}
          </Badge>
        )}
      </div>
    </div>
  );
}
