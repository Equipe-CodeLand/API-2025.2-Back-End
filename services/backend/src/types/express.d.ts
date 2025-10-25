import { Cargo } from "../enum/Cargo";

declare global {
  namespace Express {
    interface Request {
      user: {
        id: number;
        email: string;
        nome: string;
        receberEmails: boolean;
        cargo: Cargo;
      };
    }
  }
}