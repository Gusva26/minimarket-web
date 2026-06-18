const PasswordResetPage = {
  async render(container) {
    container.innerHTML = `
      <div class="login-wrapper">
        <div class="deco deco-1"></div>
        <div class="deco deco-2"></div>
        <div class="deco deco-3"></div>

        <div class="login-card">
          <div class="login-brand">
            <div class="brand-circle"><i class="fas fa-key"></i></div>
            <h2>Recuperar Contraseña</h2>
            <p>Te enviaremos un enlace a tu correo</p>
          </div>

          <div id="resetStep1">
            <form id="reset-form">
              <div class="floating-group">
                <input type="email" class="form-control" id="resetEmail" name="email" placeholder="Correo electrónico" required autocomplete="email" autofocus>
                <i class="fas fa-envelope input-icon"></i>
                <label for="resetEmail">Correo electrónico</label>
              </div>

              <div class="login-error" id="resetError">
                <i class="fas fa-exclamation-circle"></i>
                <span id="resetErrorText"></span>
              </div>

              <button type="submit" class="login-btn" id="resetBtn">
                <i class="fas fa-paper-plane"></i>
                <span>Enviar Enlace</span>
              </button>
            </form>
          </div>

          <div id="resetStep2" style="display:none;text-align:center;padding:20px 0">
            <div style="font-size:3rem;color:var(--success);margin-bottom:16px"><i class="fas fa-check-circle"></i></div>
            <h3 style="color:var(--text);margin:0 0 8px">Correo Enviado</h3>
            <p style="color:var(--text-secondary);font-size:.88rem;line-height:1.5">Revisa tu bandeja de entrada. El enlace expira en 5 minutos.</p>
          </div>

          <div class="login-footer" style="margin-top:1rem">
            <a href="#/login" style="color:var(--accent);text-decoration:none;font-size:.85rem"><i class="fas fa-arrow-left me-1"></i>Volver al inicio de sesión</a>
          </div>
        </div>
      </div>
    `;

    document.getElementById('reset-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById('resetError');
      const errorText = document.getElementById('resetErrorText');
      errorEl.classList.remove('show');
      const btn = document.getElementById('resetBtn');
      const email = document.getElementById('resetEmail').value.trim();

      if (!email) {
        errorText.textContent = 'El correo es obligatorio.';
        errorEl.classList.add('show');
        return;
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errorText.textContent = 'Ingresa un correo electrónico válido.';
        errorEl.classList.add('show');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div><span>Enviando...</span>';

      try {
        await API.post('auth/password-reset/', { email });
        document.getElementById('resetStep1').style.display = 'none';
        document.getElementById('resetStep2').style.display = 'block';
      } catch(err) {
        errorText.textContent = err.message;
        errorEl.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-paper-plane"></i><span>Enviar Enlace</span>';
      }
    });
  }
};