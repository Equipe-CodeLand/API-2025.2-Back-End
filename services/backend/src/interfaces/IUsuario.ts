export interface IUsuario {
  id: number;
  nome: string;
  status?: string; // exemplo usando enum
  username: string;
  password: string;
}