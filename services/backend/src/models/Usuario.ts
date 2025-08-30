import { IUsuario } from "../interfaces/IUsuario";
import { Status } from "../enum/Status";

export class UsuarioModel {
  private static usuarios: IUsuario[] = [];

  static criar(nome: string): IUsuario {
    const novo: IUsuario = {
      id: Date.now(),
      nome,
      status: Status.ATIVO,
    };
    this.usuarios.push(novo);
    return novo;
  }

  static listar(): IUsuario[] {
    return this.usuarios;
  }
}
