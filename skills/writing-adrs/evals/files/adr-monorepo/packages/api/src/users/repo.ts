import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export function getUserData(id: number) {
  return prisma.user.findUnique({ where: { id } });
}

export function createUser(email: string, name: string) {
  return prisma.user.create({ data: { email, name } });
}
