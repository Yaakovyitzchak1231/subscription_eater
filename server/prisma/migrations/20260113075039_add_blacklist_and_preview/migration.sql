-- AlterTable
ALTER TABLE "Subscription" ADD COLUMN "emailBody" TEXT;
ALTER TABLE "Subscription" ADD COLUMN "emailSnippet" TEXT;
ALTER TABLE "Subscription" ADD COLUMN "emailSubject" TEXT;

-- CreateTable
CREATE TABLE "Blacklist" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "term" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "Blacklist_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
