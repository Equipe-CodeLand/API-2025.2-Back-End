import { Cargo } from "../enum/Cargo";

export interface IUsuario {
  id: number;
  nome: string;
  cargo: Cargo;
  email: string;
  password: string;
  receberEmails: boolean;
}