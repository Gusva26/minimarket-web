const LoginPage = {
  async render(container) {
    container.innerHTML = `
      <div class="login-wrapper">
        <div class="login-card">
          <div class="login-brand">
            <div class="brand-circle"><i class="fas fa-store"></i></div>
            <h2>Minimarket POS</h2>
            <p>Sistema de Gestión Comercial</p>
          </div>

          <form id="login-form" autocomplete="off">
            <div class="floating-group">
              <input type="text" class="form-control" id="loginUser" placeholder="Usuario" required readonly>
              <i class="fas fa-user input-icon"></i>
              <label for="loginUser">Usuario</label>
            </div>

            <div class="floating-group">
              <input type="password" class="form-control" id="loginPass" placeholder="Contraseña" required readonly>
              <i class="fas fa-lock input-icon"></i>
              <label for="loginPass">Contraseña</label>
            </div>

            <div class="login-error" id="loginError">
              <i class="fas fa-exclamation-circle"></i>
              <span id="loginErrorText"></span>
            </div>

            <button type="submit" class="login-btn" id="loginBtn">
              <i class="fas fa-sign-in-alt"></i>
              <span>Ingresar al Sistema</span>
            </button>
          </form>

          <div style="text-align:center;margin-top:8px">
            <a href="#/password-reset" style="color:var(--text-muted);font-size:.82rem;text-decoration:none;transition:color var(--transition)">¿Olvidaste tu contraseña?</a>
          </div>

          <div class="login-footer">
            &copy; ${new Date().getFullYear()} Minimarket POS — Todos los derechos reservados
          </div>
        </div>
      </div>
    `;

    let cleared = false;
    const clr = setInterval(() => {
      const u = document.getElementById('loginUser');
      const p = document.getElementById('loginPass');
      u.value = '';
      p.value = '';
      if (!cleared) {
        u.removeAttribute('readonly');
        p.removeAttribute('readonly');
        cleared = true;
      }
    }, 50);
    setTimeout(() => {
      clearInterval(clr);
      const u = document.getElementById('loginUser');
      u.value = '';
      u.focus({ preventScroll: true });
    }, 500);

    document.getElementById('login-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById('loginError');
      const errorText = document.getElementById('loginErrorText');
      errorEl.classList.remove('show');
      const user = document.getElementById('loginUser').value.trim();
      const pass = document.getElementById('loginPass').value;

      if (!user) {
        errorText.textContent = 'El usuario es obligatorio.';
        errorEl.classList.add('show');
        return;
      }
      if (!pass) {
        errorText.textContent = 'La contraseña es obligatoria.';
        errorEl.classList.add('show');
        return;
      }

      const btn = document.getElementById('loginBtn');
      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div><span>Ingresando...</span>';

      try {
        await Auth.login(user, pass);
        window.location.hash = '#/dashboard';
      } catch(err) {
        errorText.textContent = err.message;
        errorEl.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sign-in-alt"></i><span>Ingresar al Sistema</span>';
      }
    });
  }
};
