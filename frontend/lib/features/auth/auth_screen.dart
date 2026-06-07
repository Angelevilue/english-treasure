import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/providers.dart';

class AuthScreen extends ConsumerStatefulWidget {
  const AuthScreen({super.key});

  @override
  ConsumerState<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends ConsumerState<AuthScreen> {
  final _phoneCtrl = TextEditingController();
  final _pwdCtrl = TextEditingController();
  final _nickCtrl = TextEditingController();
  bool _isRegister = false;

  Future<void> _submit() async {
    final phone = _phoneCtrl.text.trim();
    final password = _pwdCtrl.text.trim();

    if (phone.isEmpty || password.isEmpty) return;

    final auth = ref.read(authProvider.notifier);
    bool ok;
    if (_isRegister) {
      ok = await auth.register(phone, password, _nickCtrl.text.trim());
    } else {
      ok = await auth.login(phone, password);
    }

    if (!ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('操作失败，请检查手机号或密码')),
      );
      return;
    }

    if (ok && mounted) {
      context.go('/vocab');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.book, size: 64, color: Color(0xFF4A90D9)),
                const SizedBox(height: 16),
                Text(
                  _isRegister ? '注册 英语宝典' : '登录 英语宝典',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 32),
                TextField(
                  controller: _phoneCtrl,
                  decoration: const InputDecoration(
                    labelText: '手机号',
                    prefixIcon: Icon(Icons.phone_android),
                  ),
                  keyboardType: TextInputType.phone,
                ),
                const SizedBox(height: 16),
                if (_isRegister)
                  TextField(
                    controller: _nickCtrl,
                    decoration: const InputDecoration(
                      labelText: '昵称',
                      prefixIcon: Icon(Icons.person),
                    ),
                  ),
                if (_isRegister) const SizedBox(height: 16),
                TextField(
                  controller: _pwdCtrl,
                  decoration: const InputDecoration(
                    labelText: '密码',
                    prefixIcon: Icon(Icons.lock),
                  ),
                  obscureText: true,
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: _submit,
                    child: Text(_isRegister ? '注册' : '登录'),
                  ),
                ),
                TextButton(
                  onPressed: () => setState(() => _isRegister = !_isRegister),
                  child: Text(_isRegister ? '已有账号？去登录' : '没有账号？去注册'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
