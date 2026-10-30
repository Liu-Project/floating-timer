Name:           floating-timer
Version:        1.0
Release:        2%{?dist}
Summary:        悬浮倒计时/正计时工具（毛玻璃置顶悬浮）
License:        MIT
URL:            https://github.com/example/floating-timer
BuildArch:      x86_64
Requires:       xorg-x11-utils

%description
一个毛玻璃风格的悬浮置顶倒计时/正计时小工具，适合汇报、会议时放在屏幕角落查看用时。

特点:
- 始终置顶悬浮，可拖拽到任意位置
- 正计时 / 倒计时两种模式，快捷键与右键菜单操作
- 整分钟数字变红提醒，结束红色闪烁
- PyInstaller 静态打包，不依赖目标机 Python / Tkinter 环境

%prep

%build

%install
mkdir -p %{buildroot}/opt/floating-timer
install -m 0755 %{_sourcedir}/floating_timer %{buildroot}/opt/floating-timer/floating_timer
mkdir -p %{buildroot}/usr/share/applications
install -m 0644 %{_sourcedir}/floating-timer.desktop %{buildroot}/usr/share/applications/floating-timer.desktop
mkdir -p %{buildroot}/usr/share/pixmaps
install -m 0644 %{_sourcedir}/icon.png %{buildroot}/usr/share/pixmaps/floating-timer.png

%files
/opt/floating-timer/floating_timer
/usr/share/applications/floating-timer.desktop
/usr/share/pixmaps/floating-timer.png

%changelog
* Wed Oct 28 2026 ZTE AI <ai@zte.com> - 1.0-2
- 正计时去除 100 小时上限，可无限计时不再自动归零

* Wed Oct 28 2026 ZTE AI <ai@zte.com> - 1.0-1
- 首个版本：毛玻璃悬浮计时器，静态二进制 + RPM 打包
