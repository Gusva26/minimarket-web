const ResetPasswordPage = {
  async render(container, params) {
    const uid = (params && params.uid) || '';
    const token = (params && params.token) || '';

    const showInvalidLink = (message = 'El enlace de recuperación no es válido o ha expirado.') => {
      container.innerHTML = `
        <div class="login-wrapper">
          <div class="login-card" style="text-align:center;padding:40px">
            <div style="font-size:3rem;color:var(--danger);margin-bottom:16px"><i class="fas fa-exclamation-triangle"></i></div>
            <h3 style="color:var(--text);margin:0 0 8px">Enlace Inválido</h3>
            <p style="color:var(--text-secondary);font-size:.88rem">${message}</p>
            <a href="#/password-reset" class="login-btn" style="display:inline-block;width:auto;padding:12px 28px;margin-top:16px;text-decoration:none">Solicitar nuevo enlace</a>
          </div>
        </div>
      `;
    };

    if (!uid || !token) {
      showInvalidLink();
      return;
    }

    // Validar token antes de mostrar el formulario
    container.innerHTML = `
      <div class="login-wrapper">
        <div class="login-card" style="text-align:center;padding:60px">
          <div class="spinner-modern spinner-modern-lg" style="margin:0 auto"></div>
          <p style="color:var(--text-secondary);margin-top:20px">Validando enlace...</p>
        </div>
      </div>
    `;

    try {
      await API.post('auth/password-reset/validate/', { uid, token });
    } catch (err) {
      let msg = err.message;
      try {
        const parsed = JSON.parse(msg);
        if (parsed.error) msg = parsed.error;
      } catch(e) {}
      showInvalidLink(msg);
      return;
    }

    container.innerHTML = `
      <div class="login-wrapper">
        <div class="deco deco-1"></div>
        <div class="deco deco-2"></div>
        <div class="deco deco-3"></div>

        <div class="login-card">
          <div class="login-brand">
            <div class="brand-circle"><i class="fas fa-lock-open"></i></div>
            <h2>Nueva Contraseña</h2>
            <p>Ingresa tu nueva contraseña</p>
          </div>

          <div id="resetConfirmStep1">
            <form id="reset-confirm-form">
              <div class="floating-group">
                <input type="password" class="form-control" id="newPassword1" name="new_password1" placeholder="Nueva contraseña" required autocomplete="new-password" autofocus>
                <i class="fas fa-lock input-icon"></i>
                <label for="newPassword1">Nueva contraseña</label>
              </div>

              <div class="floating-group">
                <input type="password" class="form-control" id="newPassword2" name="new_password2" placeholder="Confirmar contraseña" required autocomplete="new-password">
                <i class="fas fa-check input-icon"></i>
                <label for="newPassword2">Confirmar contraseña</label>
              </div>

              <div style="font-size:.75rem;color:rgba(255,255,255,0.5);margin:-8px 0 12px 0;line-height:1.7">
                <div id="ruleLength" style="color:var(--danger)"><i class="fas fa-times me-1"></i>Mínimo 6 caracteres</div>
                <div id="ruleCommon" style="color:var(--danger)"><i class="fas fa-times me-1"></i>No puede ser una contraseña común</div>
                <div id="ruleNumeric" style="color:var(--danger)"><i class="fas fa-times me-1"></i>No puede ser completamente numérica</div>
                <div id="ruleMatch" style="color:var(--danger)"><i class="fas fa-times me-1"></i>Ambas contraseñas deben coincidir</div>
              </div>

              <div class="login-error" id="resetConfirmError">
                <i class="fas fa-exclamation-circle"></i>
                <span id="resetConfirmErrorText"></span>
              </div>

              <button type="submit" class="login-btn" id="resetConfirmBtn">
                <i class="fas fa-check"></i>
                <span>Cambiar Contraseña</span>
              </button>
            </form>
          </div>

          <div id="resetConfirmStep2" style="display:none;text-align:center;padding:20px 0">
            <div style="font-size:3rem;color:var(--success);margin-bottom:16px"><i class="fas fa-check-circle"></i></div>
            <h3 style="color:var(--text);margin:0 0 8px">Contraseña Actualizada</h3>
            <p style="color:var(--text-secondary);font-size:.88rem">Tu contraseña se ha cambiado exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.</p>
            <a href="#/login" class="login-btn" style="display:inline-block;width:auto;padding:12px 28px;margin-top:8px;text-decoration:none"><i class="fas fa-sign-in-alt me-1"></i>Iniciar Sesión</a>
          </div>

          <div class="login-footer" style="margin-top:1rem">
            <a href="#/login" style="color:var(--accent);text-decoration:none;font-size:.85rem"><i class="fas fa-arrow-left me-1"></i>Volver al inicio de sesión</a>
          </div>
        </div>
      </div>
    `;

    const pw1 = document.getElementById('newPassword1');
    const pw2 = document.getElementById('newPassword2');
    const commonPasswords = ['123456', 'password', '12345678', 'qwerty', '123456789', '12345', '1234', '111111', '1234567', 'sunshine', 'qwerty123', 'abc123', '123123', 'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master', '123qwe'];

    const ruleDefs = [
      { id: 'ruleLength', text: 'Mínimo 6 caracteres', test: v => v.length >= 6 },
      { id: 'ruleCommon', text: 'No puede ser una contraseña común', test: v => !commonPasswords.includes(v.toLowerCase()) },
      { id: 'ruleNumeric', text: 'No puede ser completamente numérica', test: v => !/^\d+$/.test(v) },
    ];

    function updateRules() {
      const v = pw1.value;
      ruleDefs.forEach(r => {
        const el = document.getElementById(r.id);
        const pass = !!v && r.test(v);
        el.style.color = pass ? 'var(--success)' : 'var(--danger)';
        el.innerHTML = (pass ? '<i class="fas fa-check me-1"></i>' : '<i class="fas fa-times me-1"></i>') + r.text;
      });
      const match = !!v && v === pw2.value;
      document.getElementById('ruleMatch').style.color = match ? 'var(--success)' : 'var(--danger)';
      document.getElementById('ruleMatch').innerHTML = (match ? '<i class="fas fa-check me-1"></i>' : '<i class="fas fa-times me-1"></i>') + 'Ambas contraseñas deben coincidir';
    }

    pw1.addEventListener('input', updateRules);
    pw2.addEventListener('input', updateRules);

    document.getElementById('reset-confirm-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const errorEl = document.getElementById('resetConfirmError');
      const errorText = document.getElementById('resetConfirmErrorText');
      errorEl.classList.remove('show');
      const btn = document.getElementById('resetConfirmBtn');

      if (!pw1.value || !pw2.value) {
        errorText.textContent = 'Ambos campos son obligatorios.';
        errorEl.classList.add('show');
        return;
      }

      if (pw1.value.length < 6) {
        errorText.textContent = 'La contraseña debe tener al menos 6 caracteres.';
        errorEl.classList.add('show');
        return;
      }

      if (commonPasswords.includes(pw1.value.toLowerCase())) {
        errorText.textContent = 'Esta contraseña es demasiado común.';
        errorEl.classList.add('show');
        return;
      }

      if (/^\d+$/.test(pw1.value)) {
        errorText.textContent = 'La contraseña no puede ser completamente numérica.';
        errorEl.classList.add('show');
        return;
      }

      if (pw1.value !== pw2.value) {
        errorText.textContent = 'Las contraseñas no coinciden.';
        errorEl.classList.add('show');
        return;
      }

      btn.disabled = true;
      btn.innerHTML = '<div class="spinner"></div><span>Cambiando...</span>';

      try {
        await API.post('auth/password-reset/confirm/', {
          uid, token,
          new_password1: pw1.value,
          new_password2: pw2.value
        });
        document.getElementById('resetConfirmStep1').style.display = 'none';
        document.getElementById('resetConfirmStep2').style.display = 'block';
      } catch(err) {
        let msg = err.message;
        try {
          const parsed = JSON.parse(msg);
          if (parsed.error) msg = parsed.error;
          else if (typeof parsed === 'object') msg = Object.values(parsed).flat().join(' ');
        } catch(e) {}
        
        errorText.textContent = msg;
        errorEl.classList.add('show');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check"></i><span>Cambiar Contraseña</span>';
      }
    });
  }
};